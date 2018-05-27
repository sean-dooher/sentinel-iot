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
		sh 'docker-compose up -d'
		sh 'docker-compose down'
                sh 'echo Testing..'
            }
        }
        stage('Deploy') {
            steps {
                sh 'echo Deploying....'
		sh 'docker-compose down'
            }
        }
    }
}
