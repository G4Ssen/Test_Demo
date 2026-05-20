terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.0"
    }
  }
}

provider "docker" {
  # Standard named pipe for Docker Desktop on Windows
  host = "npipe:////./pipe/docker_engine"
}

# Define a resource to pull a lightweight image for demo QA purposes
resource "docker_image" "nginx_demo" {
  name         = "nginx:alpine"
  keep_locally = true
}

# Create a sample Docker container to demonstrate Infrastructure as Code
resource "docker_container" "qa_demo_app" {
  image = docker_image.nginx_demo.image_id
  name  = "qa_demo_app_container"

  ports {
    internal = 80
    external = 8090
  }
}
