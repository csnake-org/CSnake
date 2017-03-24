pipeline {
    agent none
    stages {
    
        stage('Test Linux') {
            agent { label 'gcc4' }
            steps {
                checkout scm
                sh 'cmake --version'
                sh '''
export PYTHONPATH=../src
cd tests
python -m AllTests -m xml -o results.xml
                '''
            }
            post {
                always {
                    junit 'tests/results.xml'
                }
            }
        } // stage('Test Linux')
        
        stage('Test Windows') {
            agent { label 'win10' }
            steps {
                checkout scm
                bat 'cmake --version'
                bat '''
set PYTHONPATH=../src
cd tests
python -m AllTests -m xml -o results.xml
                '''
            }
            post {
                always {
                    junit 'tests/results.xml'
                }
            }
        } // stage('Test Windows')
        
    }
}