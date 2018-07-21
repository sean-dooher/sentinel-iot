pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh 'docker-compose build'
      }
    }
    stage('Test') {
      steps {
        sh 'docker-compose run interfaceserver ./run_tests.sh'
      }
    }
  }
}
