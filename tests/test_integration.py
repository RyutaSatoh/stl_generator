import unittest
import os
import time
from generator import generate_scad

class TestGeneratorIntegration(unittest.TestCase):
    def test_generate_scad_creates_files(self):
        # Define output paths
        scad_path = "output/model.scad"
        png_path = "output/preview.png"
        stl_path = "output/output.stl"

        # Ensure clean state (generate_scad does this, but good to be sure)
        # We rely on generate_scad cleanup.

        prompt = "A simple 10mm sphere"
        print(f"Running integration test with prompt: {prompt}")
        
        # This will take time as it runs the agent
        code, err = generate_scad(prompt)
        
        self.assertIsNone(err, f"Generation failed with error: {err}")
        self.assertIsNotNone(code, "Code should not be None")
        
        # Verify files exist
        self.assertTrue(os.path.exists(scad_path), "model.scad not found")
        self.assertTrue(os.path.exists(png_path), "preview.png not found")
        self.assertTrue(os.path.exists(stl_path), "output.stl not found")
        
        # Verify content basic check
        with open(scad_path, "r") as f:
            content = f.read()
            self.assertIn("sphere", content)
            
if __name__ == '__main__':
    unittest.main()
