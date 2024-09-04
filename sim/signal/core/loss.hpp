#ifndef LOSS_H
#define LOSS_H

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
#define MAT_IOR 1.5f // Material refractive index
#define MAT_A 30.0f // Material attenuation coeff (dB/m)

// FSPL = (4πdf/c)^2 -> 20*log10(4πdf/c) in dB
static float FSPL(float distance, float freq) {
    return 20 * log10(distance) + 20 * log10(freq) - 147.55;
}

static float PathLoss(const std::vector<Vec3>& path, float txFreq, short int refIndex=-1) {
    float effLen = 0.0, refLoss = 0.0;
    size_t s = 0;

    for (size_t i = 0; i < path.size() - 1; ++i, ++s) {
        float segmentDist = Vec3::Distance(path[i], path[i+1]);
        if ((short int)i == refIndex) s++;

        // presume: caster isn't inside obstacle & obstacles are closed
        if (s % 2 == 0) effLen += segmentDist;
        else effLen += (MAT_A * segmentDist); // obstacle
    }

    return FSPL(effLen, txFreq);
}

static float GetDelay(const std::vector<Vec3>& path) {
    float time = 0.0;

    for (size_t i = 0; i < path.size() - 1; ++i) {
        float segmentDist = Vec3::Distance(path[i], path[i+1]);

        if (i % 2 == 0) time += (segmentDist / LIGHT_SPEED) * AIR_IOR;
        else time += (segmentDist / LIGHT_SPEED) * MAT_IOR; // Obstacle
        // physical ray diffraction ignored for simplicity
    }
    return time * 1e9; // ns
}

static float GetRefCoe(Vec3 txPos, Vec3 rxPos, Vec3 refPos, float matPerm, bool isTM) {
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

    float a1 = Vec3::Angle(refToTx, refToRx) / 2.0f;
    float a2 = asin(c2 * sin(a1) / c1);

    if (sqrt(abs(n1 / n2)) * sin(a1) >= 1) return 1.0f;

    return (isTM) ? (sqrt(n2) * cos(a1) - sqrt(n1) * cos(a2)) /
                    (sqrt(n2) * cos(a1) + sqrt(n1) * cos(a2))
                  : (sqrt(n1) * cos(a1) - sqrt(n2) * cos(a2)) /
                    (sqrt(n1) * cos(a1) + sqrt(n2) * cos(a2));
}

static float ReflectedPathLoss(const std::vector<Vec3>& path, short int refIndex, float txFreq, float matPerm) {
    float refCoeff = GetRefCoe(path.front(), path.back(), path[refIndex], matPerm, false);
    float totalLoss = PathLoss(path, txFreq, refIndex);

    return totalLoss += 20 * -log10(abs(refCoeff));  // power reflection |Γ|^2
}

#endif
