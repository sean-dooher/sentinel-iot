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
        sh 'mkdir reports && chmod 777 reports'
        sh 'docker-compose run -v $WORKSPACE/reports:/sentinel/reports interfaceserver sh ./run_tests.sh'
        junit(testResults: reports/junit.xml, healthScaleFactor: 1)
      }
    }
  }
}