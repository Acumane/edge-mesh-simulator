#define PY_SSIZE_T_CLEAN

#include <Python.h>
#include "structmember.h"
#include <numpy/arrayobject.h>
#include "tracer.hpp"

typedef struct {
    PyObject_HEAD
    Tracer *tracer;
} RayTracerObject;

static PyObject *RecordsToPyRecords(const std::vector<Record>& records, const Vec3& txPos, const Vec3& rxPos) {
    PyObject *py_records = PyList_New(records.size());
    for (size_t i = 0; i < records.size(); ++i) {
        const Record &record = records[i];
        PyObject *py_points = PyList_New(record.points.size() + 2);  // +2 for txPos and rxPos
        
        // Add txPos at the beginning
        PyList_SetItem(py_points, 0, Py_BuildValue("(f f f)", 
            txPos.x_, txPos.y_, txPos.z_));

        // Add the points from the record
        for (size_t j = 0; j < record.points.size(); ++j) {
            PyList_SetItem(py_points, j + 1, Py_BuildValue("(f f f)", 
                record.points[j].x_, record.points[j].y_, record.points[j].z_));
        }
        
        // Add rxPos at the end (only if it's not already the last point)
        if (record.points.empty() || !(record.points.back() == rxPos)) {
            PyList_SetItem(py_points, record.points.size() + 1, Py_BuildValue("(f f f)", 
                rxPos.x_, rxPos.y_, rxPos.z_));
        } else {
            Py_SIZE(py_points)--;  // Decrease the size if we didn't add rxPos
        }
        
        // Only include refPosIndex for reflected paths
        if (record.type == RecordType::SingleReflected) {
            PyObject *py_record = Py_BuildValue("iOi", record.type, py_points, record.refPosIndex + 1);  // +1 for refPosIndex due to txPos addition
            PyList_SetItem(py_records, i, py_record);
        } else {
            PyObject *py_record = Py_BuildValue("iO", record.type, py_points);
            PyList_SetItem(py_records, i, py_record);
        }
    }
    return py_records;
}

static PyObject *Trace(RayTracerObject *self, PyObject *args) {
    PyArrayObject *txArrObj, *rxArrObj;
    if (!PyArg_ParseTuple(args, "O|O", &txArrObj, &rxArrObj))
        return NULL;

    Vec3 txPos(*(float *)PyArray_GETPTR1(txArrObj, 0),
               *(float *)PyArray_GETPTR1(txArrObj, 1),
               *(float *)PyArray_GETPTR1(txArrObj, 2));

    Vec3 rxPos(*(float *)PyArray_GETPTR1(rxArrObj, 0),
               *(float *)PyArray_GETPTR1(rxArrObj, 1),
               *(float *)PyArray_GETPTR1(rxArrObj, 2));

    return RecordsToPyRecords(self->tracer->Trace(txPos, rxPos), txPos, rxPos);
}


static PyObject *RayTracerObjectNew(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    RayTracerObject *self = (RayTracerObject *)type->tp_alloc(type, 0);
    if (self != NULL) {
        PyArrayObject *verticesArray, *trianglesArray;
        if (!PyArg_ParseTuple(args, "O|O", &verticesArray, &trianglesArray))
            return NULL;

        size_t vert_dim_n = verticesArray->dimensions[0];
        std::unordered_map<size_t, Vec3> vertices_dict;
        for (size_t i = 0; i < vert_dim_n; ++i) {
            vertices_dict[i] = Vec3(
                *(double *)PyArray_GETPTR2(verticesArray, i, 0),
                *(double *)PyArray_GETPTR2(verticesArray, i, 1),
                *(double *)PyArray_GETPTR2(verticesArray, i, 2)
            );
        }

        std::vector<Triangle *> triangles;
        size_t tri_dim_n = trianglesArray->dimensions[0];
        for (size_t i = 0; i < tri_dim_n; ++i) {
            size_t p1Idx = *(size_t *)PyArray_GETPTR2(trianglesArray, i, 0);
            size_t p2Idx = *(size_t *)PyArray_GETPTR2(trianglesArray, i, 1);
            size_t p3Idx = *(size_t *)PyArray_GETPTR2(trianglesArray, i, 2);
            triangles.push_back(new Triangle(vertices_dict[p1Idx], vertices_dict[p2Idx], vertices_dict[p3Idx]));
        }

        self->tracer = new Tracer(triangles);
    }
    return (PyObject *)self;
}

static void RayTracerObjectDealloc(RayTracerObject *self) {
    delete self->tracer;
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyMethodDef RayTracerMethods[] = {
    {"trace", (PyCFunction)Trace, METH_VARARGS, "Trace rays from tx to rx"},
    {NULL}
};

static PyTypeObject RayTracerType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "core.Tracer",
    .tp_basicsize = sizeof(RayTracerObject),
    .tp_dealloc = (destructor)RayTracerObjectDealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_doc = "Ray Tracer Objects",
    .tp_methods = RayTracerMethods,
    .tp_new = RayTracerObjectNew,
};

static PyModuleDef core_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "core",
    .m_doc = "Core",
    .m_size = -1,
};

PyMODINIT_FUNC PyInit_core(void) {
    if (PyType_Ready(&RayTracerType) < 0) return NULL;

    PyObject *module = PyModule_Create(&core_module);
    if (module == NULL) return NULL;

    Py_INCREF(&RayTracerType);
    if (PyModule_AddObject(module, "Tracer", (PyObject *)&RayTracerType) < 0) {
        Py_DECREF(&RayTracerType);
        Py_DECREF(module);
        return NULL;
    }
    return module;
}
