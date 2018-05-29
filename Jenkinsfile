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
                sh 'inserve=$(docker-compose run -d interfaceserver bash /app/run_tests.sh)'
                sh 'docker wait $inserve'
                sh 'docker cp $inserve:/app/reports ./reports'
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
        always {
            sh 'docker-compose stop interfaceserver database redis'
            sh 'docker-compose rm -f interfaceserver database redis'
        }
    }
}
