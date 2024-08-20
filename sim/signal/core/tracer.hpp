#ifndef TRACER_H
#define TRACER_H

#include <mutex>
#include <vector>
#include <math.h>

#include "record.hpp"
#include "vec3.hpp"
#include "triangle.hpp"
#include "bvh.hpp"
#include "loss.hpp"

class Tracer
{
public:
    BVH *scene_;
    std::vector<Triangle *> triangles_;

    static const int MAX_INTER = 50;

    Tracer(std::vector<Triangle *> &triangles) : triangles_(triangles)
    {
        scene_ = new BVH(triangles_);
    };

    ~Tracer()
    {
        delete scene_;
        for (Triangle *triangle : triangles_)
            delete triangle;
        triangles_.clear();
    };

    struct InterPoint {
        Vec3 pos;
        float dist;
    };

    std::vector<InterPoint> Penetrace(const Vec3& start, const Vec3& end, int maxInter = MAX_INTER) {
        std::vector<InterPoint> inters;
        Vec3 direction = Vec3(end.x_ - start.x_, end.y_ - start.y_, end.z_ - start.z_);
        direction.Normalize();
        Ray ray(start, direction);
        Vec3 curPos = start;
        float totalDist = 0.0f;
        float distToEnd = Vec3::Distance(start, end);
        int interCount = 0;

        while (interCount <= maxInter && totalDist < distToEnd) {
            float hitDist = FLT_MAX;
            if (scene_->IsIntersect(ray, hitDist)) {
                if (hitDist + totalDist < distToEnd) {
                    Vec3 hitPoint = ray.PositionAt(hitDist);
                    inters.push_back({hitPoint, totalDist + hitDist});
                    curPos = Vec3(hitPoint.x_ + direction.x_ * 0.00001f,
                                  hitPoint.y_ + direction.y_ * 0.00001f,
                                  hitPoint.z_ + direction.z_ * 0.00001f);
                    ray = Ray(curPos, direction);
                    totalDist += hitDist + 0.001f;
                    interCount++;
                } else { break; } // too close to end
            } else { break; } // miss
        }

        if (interCount > maxInter) { return {}; }
        if (inters.empty() || Vec3::Distance(inters.back().pos, end) > 0.001f) {
            inters.push_back({end, distToEnd});
        }

        return inters;
    }

    Vec3 GetMirrorPoint(Vec3 pos, Triangle *triangle)
    {
        Vec3 normal = triangle->normal_;
        float t = (Vec3::Dot(normal, triangle->p2_) - Vec3::Dot(pos, normal)) / (Vec3::Dot(normal, normal));
        return pos + normal * 2 * t;
    }

   std::vector<Record> Trace(Vec3 txPos, Vec3 rxPos)
    {
        std::vector<Record> records;

        // Direct path
        std::vector<InterPoint> directPath = Penetrace(txPos, rxPos);
        Record direct_record;
        direct_record.type = RecordType::Direct;
        direct_record.points.push_back(txPos);
        for (const auto &inter : directPath) {
            direct_record.points.push_back(inter.pos);
        }
        direct_record.refPosIndex = -1;  // no ref point
        records.push_back(direct_record);

        // Reflection
        for (Triangle *triangle : triangles_)
        {
            Vec3 mirror_point = GetMirrorPoint(txPos, triangle);

            Vec3 direction_to_rx = (rxPos - mirror_point);
            direction_to_rx.Normalize();
            Ray ref_ray(mirror_point, direction_to_rx);

            float distance;
            if (!(triangle->IsIntersect(ref_ray, distance))) continue;

            Vec3 point_on_triangle = mirror_point + direction_to_rx * (distance + 0.001f);

            std::vector<InterPoint> txToReflect = Penetrace(txPos, point_on_triangle, 4);
            if (txToReflect.empty()) { continue; }
            std::vector<InterPoint> reflectToRx = Penetrace(point_on_triangle, rxPos, 4);
            if (reflectToRx.empty()) { continue; }

            Record reflect_record;
            reflect_record.type = RecordType::SingleReflected;
            reflect_record.points.push_back(txPos);
            for (const auto &inter : txToReflect) {
                reflect_record.points.push_back(inter.pos);
            }
            reflect_record.refPosIndex = reflect_record.points.size() - 1;
            for (const auto &inter : reflectToRx) {
                reflect_record.points.push_back(inter.pos);
            }
            records.push_back(reflect_record);
        }
        return records;
    };
};

#endif //!TRACER_H