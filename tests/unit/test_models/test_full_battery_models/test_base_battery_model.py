#
# Tests for the base battery model class
#
import pybamm
import unittest


class TestBaseBatteryModel(unittest.TestCase):
    def test_process_parameters_and_discretise(self):
        model = pybamm.lithium_ion.SPM()
        c = pybamm.Parameter("Negative electrode thickness [m]") * pybamm.Variable(
            "X-averaged negative particle concentration",
            domain="negative particle",
            auxiliary_domains={"secondary": "current collector"},
        )
        processed_c = model.process_parameters_and_discretise(c)
        self.assertIsInstance(processed_c, pybamm.Multiplication)
        self.assertIsInstance(processed_c.left, pybamm.Scalar)
        self.assertIsInstance(processed_c.right, pybamm.StateVector)

    def test_default_geometry(self):
        var = pybamm.standard_spatial_vars

        model = pybamm.BaseBatteryModel({"dimensionality": 0})
        self.assertEqual(
            model.default_geometry["current collector"]["primary"][var.z][
                "position"
            ].id,
            pybamm.Scalar(1).id,
        )
        model = pybamm.BaseBatteryModel({"dimensionality": 1})
        self.assertEqual(
            model.default_geometry["current collector"]["primary"][var.z]["min"].id,
            pybamm.Scalar(0).id,
        )
        model = pybamm.BaseBatteryModel({"dimensionality": 2})
        self.assertEqual(
            model.default_geometry["current collector"]["primary"][var.y]["min"].id,
            pybamm.Scalar(0).id,
        )

    def test_default_submesh_types(self):
        model = pybamm.BaseBatteryModel({"dimensionality": 0})
        self.assertTrue(
            issubclass(
                model.default_submesh_types["current collector"], pybamm.SubMesh0D
            )
        )
        model = pybamm.BaseBatteryModel({"dimensionality": 1})
        self.assertTrue(
            issubclass(
                model.default_submesh_types["current collector"],
                pybamm.Uniform1DSubMesh,
            )
        )
        model = pybamm.BaseBatteryModel({"dimensionality": 2})
        self.assertTrue(
            issubclass(
                model.default_submesh_types["current collector"], pybamm.Scikit2DSubMesh
            )
        )

    def test_default_spatial_methods(self):
        model = pybamm.BaseBatteryModel({"dimensionality": 0})
        self.assertTrue(
            issubclass(
                model.default_spatial_methods["current collector"],
                pybamm.ZeroDimensionalMethod,
            )
        )
        model = pybamm.BaseBatteryModel({"dimensionality": 1})
        self.assertTrue(
            issubclass(
                model.default_spatial_methods["current collector"], pybamm.FiniteVolume
            )
        )
        model = pybamm.BaseBatteryModel({"dimensionality": 2})
        self.assertTrue(
            issubclass(
                model.default_spatial_methods["current collector"],
                pybamm.ScikitFiniteElement,
            )
        )

    def test_bad_options(self):
        with self.assertRaisesRegex(pybamm.OptionError, "option"):
            pybamm.BaseBatteryModel({"bad option": "bad option"})
        with self.assertRaisesRegex(pybamm.OptionError, "current collector model"):
            pybamm.BaseBatteryModel({"current collector": "bad current collector"})
        with self.assertRaisesRegex(pybamm.OptionError, "thermal model"):
            pybamm.BaseBatteryModel({"thermal": "bad thermal"})
        with self.assertRaisesRegex(
            pybamm.OptionError, "Dimension of current collectors"
        ):
            pybamm.BaseBatteryModel({"dimensionality": 5})
        with self.assertRaisesRegex(pybamm.OptionError, "surface form"):
            pybamm.BaseBatteryModel({"surface form": "bad surface form"})
        with self.assertRaisesRegex(pybamm.OptionError, "particle model"):
            pybamm.BaseBatteryModel({"particle": "bad particle"})

    def test_build_twice(self):
        model = pybamm.lithium_ion.SPM()  # need to pick a model to set vars and build
        with self.assertRaisesRegex(pybamm.ModelError, "Model already built"):
            model.build_model()

    def test_get_coupled_variables(self):
        model = pybamm.lithium_ion.BaseModel()
        model.submodels["current collector"] = pybamm.current_collector.Uniform(
            model.param
        )
        with self.assertRaisesRegex(pybamm.ModelError, "Submodel"):
            model.build_model()


if __name__ == "__main__":
    print("Add -v for more debug output")
    import sys

    if "-v" in sys.argv:
        debug = True
    pybamm.settings.debug_mode = True
    unittest.main()
