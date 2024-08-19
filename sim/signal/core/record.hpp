#ifndef RECORD_H
#define RECORD_H

#include <vector>
#include "vec3.hpp"

enum RecordType
{
    Direct = 1,
    SingleReflected = 2,
};

struct Record
{
    RecordType type;
    std::vector<Vec3> points;
    short int refPosIndex;
};

#endif // !RECORD_H