pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'echo Building..'
                sh 'docker-compose build'
            }
        }
        stage('Test') {
            steps {
                sh 'docker-compose run -d database'
                sh 'docker-compose run -d redis'
                sh 'docker-compose run interfaceserver bash /app/run_tests.sh'
                sh 'docker-compose stop interfaceserver database redis'
                sh 'docker-compose rm -f interfaceserver database redis'
                sh 'echo Testing..'
            }
        }
        stage('Deploy') {
            steps {
                sh 'echo Deploying....'
            }
        }
    }
    post {
        failure {
            sh 'docker-compose stop interfaceserver database redis'
            sh 'docker-compose rm -f interfaceserver database redis'
        }
    }
}
