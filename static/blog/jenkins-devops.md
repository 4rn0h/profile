# Automating CI/CD with Jenkins and Docker

In this blog, I show how I used Jenkins pipelines and Docker to automate my Python deployments.

## Pipeline Setup

- Source control with GitHub
- Jenkins build triggers on push
- Docker containers for staging/testing

## Jenkinsfile Example

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'docker build -t myapp .'
            }
        }
        stage('Test') {
            steps {
                sh 'pytest tests/'
            }
        }
        stage('Deploy') {
            steps {
                sh './deploy.sh'
            }
        }
    }
}
```

## Tips

- Automate everything.
- Use Docker for clean builds.
