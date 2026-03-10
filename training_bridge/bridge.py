import os
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KaggleBridge:
    """
    Bridge for dynamically triggering Kaggle kernels for model training.
    """
    def __init__(self, kernel_id: str):
        self.kernel_id = kernel_id
        # Use absolute path to the project root to find the target_kernel_folder
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.target_folder = os.path.join(self.project_root, "target_kernel_folder")
        
    def flash_training_run(self, dataset_path: str, script_args: str = ""):
        """
        Pushes and executes a script onto a Kaggle Kernel instance.
        """
        logger.info(f"Preparing to Flash training run on Kaggle kernel: {self.kernel_id}")
        logger.info(f"Dataset targeted: {dataset_path}")
        
        if not os.path.exists(self.target_folder):
            logger.error(f"Target folder not found: {self.target_folder}")
            return

        command = [
            "kaggle", "kernels", "push",
            "-p", self.target_folder
        ]
        
        logger.info(f"Executing: {' '.join(command)}")
        try:
            # We will run the real subprocess call to execute the kaggle push
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            logger.info(f"Kaggle CLI Response:\n{result.stdout}")
            logger.info("Kaggle API push: SUCCESS. Kernel is now running.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to flash training run. Return code: {e.returncode}")
            logger.error(f"stdout: {e.stdout}")
            logger.error(f"stderr: {e.stderr}")
        except Exception as e:
            logger.error(f"Unexpected error when flashing training run: {e}")

if __name__ == "__main__":
    # Updated to match the ID in your kernel-metadata.json
    bridge = KaggleBridge(kernel_id="aniketshenoy2012ae/antariksh-v1")
    bridge.flash_training_run(dataset_path="/kaggle/input/indic-dataset")
