#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "tracer.hpp"
#include "loss.hpp"

namespace py = pybind11;

PYBIND11_MODULE(signal, m) {
    py::class_<Tracer>(m, "Tracer")
        .def(py::init([](py::array_t<float> vertices, py::array_t<size_t> faces) {
            py::buffer_info vBuf = vertices.request(), fBuf = faces.request();

            float* v = static_cast<float*>(vBuf.ptr);
            size_t* f = static_cast<size_t*>(fBuf.ptr);

            std::vector<Triangle*> triangles;
            for (py::ssize_t i = 0; i < fBuf.shape[0]; ++i) {
                size_t i1 = f[i*3], i2 = f[i*3 + 1], i3 = f[i*3 + 2];
                triangles.push_back(new Triangle(
                    Vec3(v[i1*3], v[i1*3 + 1], v[i1*3 + 2]),
                    Vec3(v[i2*3], v[i2*3 + 1], v[i2*3 + 2]),
                    Vec3(v[i3*3], v[i3*3 + 1], v[i3*3 + 2])
                ));
            }
            return new Tracer(triangles);
        }))
        .def("trace", [](Tracer& self, py::array_t<float> start, py::array_t<float> end) {
            auto s = start.unchecked<1>(), e = end.unchecked<1>();
            auto records = self.Trace(Vec3(s(0), s(1), s(2)), Vec3(e(0), e(1), e(2)));
            
            py::list result;
            for (const auto& record : records) {
                py::list points;
                for (const auto& point : record.points) {
                    points.append(py::make_tuple(point.x_, point.y_, point.z_));
                }
                result.append(py::make_tuple(static_cast<int>(record.type), points, record.refPosIndex));
            }
            return result;
        });

    m.def("calcLoss", [](int type, py::list points, short int refIndex, float freq, float perm) {
        std::vector<Vec3> path;
        for (auto point : points) {
            py::tuple t = point.cast<py::tuple>();
            path.emplace_back(t[0].cast<float>(), t[1].cast<float>(), t[2].cast<float>());
        }
        
        float loss, delay;
        if (type == 1) {
            loss = PathLoss(path, freq);
            delay = GetDelay(path);
        }
        else if (type == 2) {
            loss = ReflectedPathLoss(path, refIndex, freq, perm);
            delay = GetDelay(path);
        }
        return py::make_tuple(loss, delay);
    });
}
