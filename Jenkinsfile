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
        junit 'reports/junit.xml'
        cobertura autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'reports/coverage.xml', conditionalCoverageTargets: '70, 0, 0', failUnhealthy: false, failUnstable: false, lineCoverageTargets: '80, 0, 0', maxNumberOfBuilds: 0, methodCoverageTargets: '80, 0, 0', onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false
      }
    }
    stage('Publish') {
      when {
        branch 'master'
      }
      steps {
        sh 'docker tag sentinel$BUILD_ID seandooher/sentinel-iot'
        sh 'docker push seandooher/sentinel-iot'
      }
    }
  }
  post {
    always {
      sh 'docker-compose down -v'
      sh 'docker container prune -f'
      sh 'docker network prune -f'
    }
  }
}