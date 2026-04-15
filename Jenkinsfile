pipeline {
    agent any

    tools {
        // This must match the name you gave in Global Tool Configuration
        maven 'Maven3' 
    }

    stages {
        stage('Clone') {
            steps {
                // Clones your specific repository
                git 'https://github.com/LikithKumar0112/Jenkins-demo.git'
            }
        }

        stage('Build') {
            steps {
                // 'clean package' compiles code and creates a JAR
                sh 'mvn clean package' 
            }
        }

        stage('Test') {
            steps {
                // Runs unit tests defined in your project
                sh 'mvn test'
            }
            post {
                always {
                    // Archives test results in Jenkins UI
                    junit 'target/surefire-reports/*.xml'
                }
            }
        }
    }
}
