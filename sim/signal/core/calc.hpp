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
#define AIR_IOR 1.00029f  // Index of Refraction

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

#endif