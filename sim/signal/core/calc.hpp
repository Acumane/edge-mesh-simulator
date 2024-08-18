#ifndef CALC_H
#define CALC_H

#include <math.h>

#include <algorithm>
#include <cfloat>
#include <set>
#include <utility>
#include <vector>

#include "record.hpp"
#include "vec3.hpp"

#define LIGHT_SPEED 299792458.0f
#define AIR_IOR 1.00029f

static float GetDelay(std::vector<Vec3> points, float speed)
{
    float total_distance = 0.0f;
    for (size_t i = 0; i < points.size() - 1; ++i)
    {
        total_distance += Vec3::Distance(points[i], points[i + 1]);
    }
    return float(total_distance / speed);
}

static float SegmentLoss(float distance, float freq) {
    return 20.0f * log10(distance) + 20.0f * log10(freq) - 147.55f;
}

static float ObstacleLoss(float distance, float freq) { // PLACEHOLDER
    return 10.0f * distance * (freq / 1e9); // 10 dB per meter @ 1GHz, scaled w/ freq
}

static float PathLoss(const std::vector<Vec3>& path, float txFreq) {
    float totalLoss = 0.0f;
    float totalDistance = 0.0f;

    for (size_t i = 0; i < path.size() - 1; ++i) {
        float segmentDistance = Vec3::Distance(path[i], path[i+1]);
        totalDistance += segmentDistance;

        if (i % 2 == 0) {
            totalLoss += SegmentLoss(segmentDistance, txFreq);
        } else {
            totalLoss += ObstacleLoss(segmentDistance, txFreq);
        }
    }

    totalLoss += 20.0f * log10(totalDistance) + 20.0f * log10(txFreq) - 147.55f;

    return totalLoss;
}

static float GetRefCoe(Vec3 txPos, Vec3 rxPos, Vec3 refPos, float matPerm, bool isTM)
{
    Vec3 refToTx = txPos - refPos;
    refToTx.Normalize();
    Vec3 refToRx = rxPos - refPos;
    refToRx.Normalize();

    // IOR - Index of Refraction
    // Relative permittivity according to ITU-R, P.2040-1. (for 1-100 GHz)
    constexpr float n1 = AIR_IOR; // Air IOR
    float n2 = matPerm;
    constexpr float c = LIGHT_SPEED;

    float c1 = c / sqrt(n1);
    float c2 = c / sqrt(n2);

    float angle_1 = Vec3::Angle(refToTx, refToRx) / 2.0f;
    float angle_2 = asin(c2 * sin(angle_1) / c1);

    if (sqrt(abs(n1 / n2)) * sin(angle_1) >= 1)
        return 1.0f;

    float coe = (isTM) ? (sqrt(n2) * cos(angle_1) - sqrt(n1) * cos(angle_2)) /
                             (sqrt(n2) * cos(angle_1) + sqrt(n1) * cos(angle_2))
                       : (sqrt(n1) * cos(angle_1) - sqrt(n2) * cos(angle_2)) /
                             (sqrt(n1) * cos(angle_1) + sqrt(n2) * cos(angle_2));
    return coe;
}

static float ReflectedPathLoss(const Record& record, float txFreq, float matPerm) {
    Vec3 txPos = record.points.front();
    Vec3 rxPos = record.points.back();
    Vec3 refPos = record.points[record.refPosIndex];

    float refCoeff = GetRefCoe(txPos, rxPos, refPos, matPerm, false); // assuming all rays are TE

    float totalLoss = PathLoss(record.points, txFreq);

    totalLoss -= 20.0f * log10(abs(refCoeff));

    return totalLoss;
}

static float GetVValue(Vec3 txPos, Vec3 rxPos, Vec3 edgePos, float txFreq)
{
    float r1 = Vec3::Distance(txPos, edgePos);
    float r2 = Vec3::Distance(edgePos, rxPos);
    float s1_s2 = Vec3::Distance(txPos, rxPos);
    Vec3 tx_to_rx_dir = (rxPos - txPos);
    tx_to_rx_dir.Normalize();
    Vec3 tx_to_edge_dir = (edgePos - txPos);
    tx_to_edge_dir.Normalize();
    float angle = Vec3::Angle(tx_to_edge_dir, tx_to_rx_dir);
    float h = r1 * sin(angle);
    float wave_length = LIGHT_SPEED / txFreq;
    return h * sqrt((2 * s1_s2) / (wave_length * r1 * r2));
}

static float GetCValue(float v)
{
    return 6.9 + 20.0 * log10(sqrt(pow(v - 0.1f, 2) + 1) + v - 0.1f);
}

static float DiffractedPathLoss(Vec3 txPos, Vec3 rxPos, std::vector<Vec3> edges, float txFreq)
{
    // Diffraction Loss is calculate according to the multiple knife edges by
    // Ensure the order of edges
    Vec3::ReorderEdges(txPos, edges);
    float segmentDistance = Vec3::Distance(txPos, rxPos);

    float pl = SegmentLoss(segmentDistance, txFreq);
    if (edges.size() == 0)
        return pl;
    if (edges.size() == 1)
    {
        pl += GetCValue(GetVValue(txPos, rxPos, edges[0], txFreq));
        return pl;
    }

    if (edges.size() == 2)
    {
        Vec3 &nearTxEdge = edges[0];
        Vec3 &nearRxEdge = edges[1];
        float nearTxEdgeV = GetVValue(txPos, rxPos, nearTxEdge, txFreq);
        float nearRxEdgeV = GetVValue(txPos, rxPos, nearRxEdge, txFreq);
        float mainDiffractionLoss, supportDiffractionLoss;
        if (nearTxEdgeV > nearRxEdgeV)
        {
            mainDiffractionLoss = GetCValue(nearTxEdgeV);
            supportDiffractionLoss = GetCValue(GetVValue(nearTxEdge, rxPos, nearRxEdge, txFreq));
        }
        else
        {
            mainDiffractionLoss = GetCValue(nearRxEdgeV);
            supportDiffractionLoss = GetCValue(GetVValue(txPos, nearRxEdge, nearTxEdge, txFreq));
        }
        if (isnan(supportDiffractionLoss))
            supportDiffractionLoss = 0.0;
        //  printf("main loss: %.2f, support loss: %.2f\n", mainDiffractionLoss, supportDiffractionLoss);

        pl += mainDiffractionLoss + supportDiffractionLoss;
        return pl;
    }

    // triple edges
    Vec3 nearTxEdge, centerEdge, nearRxEdge;
    if (edges.size() == 3)
    {
        nearTxEdge = edges[0];
        centerEdge = edges[1];
        nearRxEdge = edges[2];
    }
    else
    {
        // pick up highest v edges
        std::set<std::pair<float, Vec3> > ordered_v;
        for (Vec3 &edge : edges)
        {
            ordered_v.insert({GetVValue(txPos, txPos, edge, txFreq), edge});
        }
        std::vector<Vec3> ordered_edges;
        for (auto &[v, edge] : ordered_v)
            ordered_edges.push_back(edge);
        std::vector<Vec3> top_edges;
        top_edges.push_back(ordered_edges[0]);
        top_edges.push_back(ordered_edges[1]);
        top_edges.push_back(ordered_edges[2]);

        Vec3::ReorderEdges(txPos, top_edges);
        nearTxEdge = top_edges[0];
        centerEdge = top_edges[1];
        nearRxEdge = top_edges[2];
    }

    float nearTxEdgeV = GetVValue(txPos, rxPos, nearTxEdge, txFreq);
    float centerEdgeV = GetVValue(txPos, rxPos, centerEdge, txFreq);
    float nearRxEdgeV = GetVValue(txPos, rxPos, nearRxEdge, txFreq);
    float maxEdgeV = std::max({nearTxEdgeV, centerEdgeV, nearRxEdgeV});
    float mainDiffractionLoss, supportDiffractionLoss1, supportDiffractionLoss2;
    if (nearTxEdgeV == maxEdgeV)
    {
        // near tx edge is main edge
        mainDiffractionLoss = GetCValue(nearTxEdgeV);
        supportDiffractionLoss1 = GetCValue(GetVValue(nearTxEdge, nearRxEdge, centerEdge, txFreq));
        supportDiffractionLoss2 = GetCValue(GetVValue(centerEdge, rxPos, nearRxEdge, txFreq));
    }
    else if (nearRxEdgeV == maxEdgeV)
    {
        // near rx edge is main edge
        mainDiffractionLoss = GetCValue(nearRxEdgeV);
        supportDiffractionLoss1 = GetCValue(GetVValue(txPos, centerEdge, nearTxEdge, txFreq));
        supportDiffractionLoss2 = GetCValue(GetVValue(nearTxEdge, nearRxEdge, centerEdge, txFreq));
    }
    else
    {
        // center edge is main edge
        mainDiffractionLoss = GetCValue(centerEdgeV);
        supportDiffractionLoss1 = GetCValue(GetVValue(txPos, centerEdge, nearTxEdge, txFreq));
        supportDiffractionLoss2 = GetCValue(GetVValue(centerEdge, rxPos, nearRxEdge, txFreq));
    }
    if (isnan(supportDiffractionLoss1))
        supportDiffractionLoss1 = 0.0f;
    if (isnan(supportDiffractionLoss2))
        supportDiffractionLoss2 = 0.0f;
    //printf("main loss: %.2f, support loss 1: %.2f, support loss 2: %.2f\n", mainDiffractionLoss,
    //              supportDiffractionLoss1, supportDiffractionLoss2);
    pl += mainDiffractionLoss + supportDiffractionLoss1 + supportDiffractionLoss2;

    return pl;
}

static float GetTotalPathLoss(Vec3 txPos, Vec3 rxPos,
                              float txFreq, float matPerm,
                              std::vector<Record>& records)
{
    float total_loss_linear = 0.0f;
    for (const Record& record : records)
    {
        float loss_dB = 0.0f;
        if (record.type == RecordType::Direct)
        {
            if (record.points.empty()) {
                loss_dB = PathLoss({txPos, rxPos}, txFreq);
            } else {
                std::vector<Vec3> path = {txPos};
                path.insert(path.end(), record.points.begin(), record.points.end());
                path.push_back(rxPos);
                loss_dB = PathLoss(path, txFreq);
            }
        }
        else if (record.type == RecordType::SingleReflected)
        {
            loss_dB = ReflectedPathLoss(record, txFreq, matPerm);
        }
        else if (record.type == RecordType::Diffracted)
        {
            loss_dB = DiffractedPathLoss(txPos, rxPos, record.points, txFreq);
        }
        total_loss_linear += pow(10.0f, -loss_dB / 10.0f);
    }
    // return the total loss in dB
    return (float)(-10 * log10(total_loss_linear));
}

#endif