"""
Hugging Face Hub module
"""

import os

import huggingface_hub

from huggingface_hub.utils import RepositoryNotFoundError

from .base import Cloud


class HuggingFaceHub(Cloud):
    """
    Hugging Face Hub cloud provider.
    """

    def metadata(self, path=None):
        try:
            # If this is an archive file path, get file metadata
            if self.isarchive(path):
                url = huggingface_hub.hf_hub_url(
                    repo_id=self.config["container"], filename=os.path.basename(path), revision=self.config.get("revision")
                )

                return huggingface_hub.get_hf_file_metadata(url=url, token=self.config.get("token"))

            # Otherwise return repository metadata
            return huggingface_hub.model_info(repo_id=self.config["container"], revision=self.config.get("revision"), token=self.config.get("token"))

        except RepositoryNotFoundError:
            return None

    def load(self, path=None):
        # Download archvie file and return local path
        if self.isarchive(path):
            return huggingface_hub.hf_hub_download(
                repo_id=self.config["container"],
                filename=os.path.basename(path),
                revision=self.config.get("revision"),
                cache_dir=self.config.get("cache"),
                token=self.config.get("token"),
            )

        # Download repository and return cached path
        return huggingface_hub.snapshot_download(
            repo_id=self.config["container"], revision=self.config.get("revision"), cache_dir=self.config.get("cache"), token=self.config.get("token")
        )

    def save(self, path):
        # Get or create repository
        huggingface_hub.create_repo(
            repo_id=self.config["container"], token=self.config.get("token"), private=self.config.get("private", True), exist_ok=True
        )

        # Upload files
        for f in self.listfiles(path):
            huggingface_hub.upload_file(
                repo_id=self.config["container"],
                revision=self.config.get("revision"),
                token=self.config.get("token"),
                path_or_fileobj=f,
                path_in_repo=os.path.basename(f),
            )
