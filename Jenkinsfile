pipeline {
    agent none
    environment {
        scmUrl = 'https://github.com/csnake-org/CSnake.git'
        testShell = 'cmake --version; export PYTHONPATH=../src; cd tests; python -m AllTests -m xml -o results.xml'
        testBat = 'cmake --version & set PYTHONPATH=../src & cd tests & python -m AllTests -m xml -o results.xml'
        testResults = 'tests/results.xml'
    }
    stages {
        stage('Test') {
            parallel {
                stage('linux cmake28') {
                    agent { label 'linux && cmake28' }
                    steps {
                        git scmUrl
                        sh "${env.testShell}"
                    }
                    post {
                        always {
                            junit testResults
                        }
                    }
                }
                stage('linux cmake35') {
                    agent { label 'linux && cmake35' }
                    steps {
                        git scmUrl
                        sh "${env.testShell}"
                    }
                    post {
                        always {
                            junit testResults
                        }
                    }
                }
                stage('linux cmake38') {
                    agent { label 'linux && cmake38' }
                    steps {
                        git scmUrl
                        sh "${env.testShell}"
                    }
                    post {
                        always {
                            junit testResults
                        }
                    }
                }
                stage('windows cmake38') {
                    agent { label 'windows && cmake38' }
                    steps {
                        git scmUrl
                        bat "${env.testBat}"
                    }
                    post {
                        always {
                            junit testResults
                        }
                    }
                }
            } // parallel
        } // stage('Test')
        
        stage('Doc') {
            agent { label 'linux' }
            when { branch 'master' }
            steps {
                sh 'cd doc; doxygen --version; doxygen Doxyfile.doxy'
            } // steps
            post {
                success {
                    // publish html
                    publishHTML target: [
                        allowMissing: false,
                        alwaysLinkToLastBuild: false,
                        keepAll: true,
                        reportDir: 'doc/html',
                        reportFiles: 'index.html',
                        reportName: 'Code Documentation'
                    ]
                }
            }
        } // stage('Doc')
    }
}