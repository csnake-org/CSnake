pipeline {
    agent none
    environment { 
        test_shell = 'cmake --version; export PYTHONPATH=../src; cd tests; python -m AllTests -m xml -o results.xml'
        test_bat = 'cmake --version & set PYTHONPATH=../src & cd tests & python -m AllTests -m xml -o results.xml'
    }
    stages {
        stage('Start') {
            steps {
                echo 'Starting CSnake build...'
            } // steps
        } // stage('Start')
    
        stage('Test') {
            steps {
                parallel (
                
                    'linux cmake28': {
                        node( 'linux && cmake28' ) {
                            git 'https://github.com/csnake-org/CSnake.git'
                            sh "${env.test_shell}"
                        }
                    },
                    
                    'linux cmake30': {
                        node( 'linux && cmake30' ) {
                            git 'https://github.com/csnake-org/CSnake.git'
                            sh "${env.test_shell}"
                        }
                    },

                    'linux cmake34': {
                        node( 'linux && cmake34' ) {
                            git 'https://github.com/csnake-org/CSnake.git'
                            sh "${env.test_shell}"
                        }
                    },

                    'windows cmake28': {
                        node( 'win10 && cmake28' ) {
                            git 'https://github.com/csnake-org/CSnake.git'
                            bat "${env.test_bat}"
                        }
                    }
                    
                ) // parallel
            } // steps
        } // stage('Test')
        
        stage('Doc') {
            agent { label 'linux' }
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
    post {
        always {
            node( 'linux && cmake28' ) {
                junit 'tests/results.xml'
            }
            node( 'linux && cmake30' ) {
                junit 'tests/results.xml'
            }
            node( 'linux && cmake34' ) {
                junit 'tests/results.xml'
            }
            node( 'win10 && cmake28' ) {
                junit 'tests/results.xml'
            }
        }
    }
}