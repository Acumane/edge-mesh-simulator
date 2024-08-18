#define PY_SSIZE_T_CLEAN

#include <Python.h>

#include "calc.hpp"

static PyObject *GetDirectLoss(PyObject *self, PyObject *args)
{
    PyObject *txPosObj;
    PyObject *rxPosObj;
    float txFreq;
    if (!PyArg_ParseTuple(args, "O|O|f", &txPosObj, &rxPosObj, &txFreq))
        return NULL;

    Vec3 txPos;
    txPos.x_ = (float)PyFloat_AsDouble(PyList_GetItem(txPosObj, 0));
    txPos.y_ = (float)PyFloat_AsDouble(PyList_GetItem(txPosObj, 1));
    txPos.z_ = (float)PyFloat_AsDouble(PyList_GetItem(txPosObj, 2));

    Vec3 rxPos;
    rxPos.x_ = (float)PyFloat_AsDouble(PyList_GetItem(rxPosObj, 0));
    rxPos.y_ = (float)PyFloat_AsDouble(PyList_GetItem(rxPosObj, 1));
    rxPos.z_ = (float)PyFloat_AsDouble(PyList_GetItem(rxPosObj, 2));

    float segmentDistance = Vec3::Distance(txPos, rxPos);

    std::vector<Vec3> points;
    points.push_back(txPos);
    points.push_back(rxPos);

    return Py_BuildValue("f f", SegmentLoss(segmentDistance, txFreq), GetDelay(points, LIGHT_SPEED));
}

static PyObject *GetReflectionLoss(PyObject *self, PyObject *args)
{
    PyObject *txPosObj;
    PyObject *rxPosObj;
    PyObject *refPosObj;
    float txFreq;
    float matPerm;
    if (!PyArg_ParseTuple(args, "O|O|O|f|f", &txPosObj, &rxPosObj, &refPosObj, &txFreq, &matPerm))
        return NULL;

    Vec3 txPos;
    txPos.x_ = (float)PyFloat_AsDouble(PyList_GetItem(txPosObj, 0));
    txPos.y_ = (float)PyFloat_AsDouble(PyList_GetItem(txPosObj, 1));
    txPos.z_ = (float)PyFloat_AsDouble(PyList_GetItem(txPosObj, 2));

    Vec3 rxPos;
    rxPos.x_ = (float)PyFloat_AsDouble(PyList_GetItem(rxPosObj, 0));
    rxPos.y_ = (float)PyFloat_AsDouble(PyList_GetItem(rxPosObj, 1));
    rxPos.z_ = (float)PyFloat_AsDouble(PyList_GetItem(rxPosObj, 2));

    Vec3 refPos;
    refPos.x_ = (float)PyFloat_AsDouble(PyList_GetItem(refPosObj, 0));
    refPos.y_ = (float)PyFloat_AsDouble(PyList_GetItem(refPosObj, 1));
    refPos.z_ = (float)PyFloat_AsDouble(PyList_GetItem(refPosObj, 2));

    Record record;
    record.type = RecordType::SingleReflected;
    record.points = {txPos, refPos, rxPos};
    record.refPosIndex = 1;  // refPos is at index 1 in points vector

    float loss = ReflectedPathLoss(record, txFreq, matPerm);
    float delay = GetDelay(record.points, LIGHT_SPEED);

    return Py_BuildValue("f f", loss, delay);
}

static PyMethodDef CalcFunctions[] = {
    {"directLoss", (PyCFunction)GetDirectLoss, METH_VARARGS, "Calculate loss along direct path"},
    {"reflectLoss", (PyCFunction)GetReflectionLoss, METH_VARARGS, "Calculate loss along reflected path"},
    {NULL}
};

static PyModuleDef CalcModule = {
    PyModuleDef_HEAD_INIT,
    .m_name = "calc",
    .m_doc = "The path loss calculator module",
    .m_size = -1,
    .m_methods = CalcFunctions,
};

PyMODINIT_FUNC PyInit_calc(void)
{
    PyObject *m = PyModule_Create(&CalcModule);
    if (m == NULL)
        return NULL;

    return m;
}
