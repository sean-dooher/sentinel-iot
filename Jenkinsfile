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
                sh 'docker-compose run interfaceserver /app/run_tests.sh'
                sh 'docker-compose stop interfaceserver'
                sh 'docker-compose stop database'
                sh 'docker-compose stop redis'
                sh 'echo Testing..'
            }
        }
        stage('Deploy') {
            steps {
                sh 'echo Deploying....'
            }
        }
    }
}
