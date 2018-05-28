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
		sh 'docker-compose run interfaceserver /app/manage.py test'
		sh 'docker-compose stop interfaceserver'
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
