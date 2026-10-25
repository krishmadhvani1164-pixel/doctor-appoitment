pipeline {
    agent any

    environment {
        IMAGE = "krissh1704/doctor-appointment"
        TAG   = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build and Test') {
            steps {
                sh '''
                  docker run --rm -v "$PWD":/app -w /app python:3.11-slim \
                    sh -c "pip install --no-cache-dir -r requirements.txt && pytest"
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t $IMAGE:$TAG -t $IMAGE:latest .'
            }
        }

        stage('Push Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                                 usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
                    sh '''
                      echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
                      docker push $IMAGE:$TAG
                      docker push $IMAGE:latest
                      docker logout
                    '''
                }
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh '''
                  sed "s|IMAGE_PLACEHOLDER|$IMAGE:$TAG|g" k8s/deployment.yaml | kubectl apply -f -
                  kubectl apply -f k8s/service.yaml
                  kubectl rollout status deployment/doctor-appointment --timeout=120s
                '''
            }
        }

        stage('Verification') {
            steps {
                sh '''
                  kubectl get pods
                  kubectl get deployment
                  kubectl get svc
                '''
            }
        }
    }
}
