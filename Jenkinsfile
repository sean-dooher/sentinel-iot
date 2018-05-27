pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Building..'
		docker-compose build
            }
        }
        stage('Test') {
            steps {
		docker-compose up
                echo 'Testing..'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
            }
        }
    }
}
