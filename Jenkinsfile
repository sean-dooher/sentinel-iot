pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh 'docker-compose build'
        sh 'mkdir reports && chmod o+w reports'
      }
    }
    stage('Test') {
      steps {
        sh ' docker-compose run -v $WORKSPACE/reports:/sentinel/reports interfaceserver sh ./run_tests.sh'
        junit reports/junit.xml
      }
    }
  }
}
