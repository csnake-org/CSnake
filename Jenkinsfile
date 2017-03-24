pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Test') {
            steps {
                echo 'cmake --version'
                sh """
export PYTHONPATH=../src
cd tests
python -m AllTests -m xml -o results.xml
                """
            }
        }
    }
    post {
        always {
            junit 'tests/results.xml'
        }
    }
}