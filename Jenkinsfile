pipeline {
  agent any
  environment {
    ID = "${env.GIT_BRANCH}-${env.BUILD_ID}";
  }
  stages {
    stage('Build') {
      steps {
        sh 'docker-compose -p $ID build'
      }
    }
    stage('Test') {
      steps {
        sh 'mkdir reports && chmod 777 reports'
        sh 'docker-compose -p $ID run -v $WORKSPACE/reports:/sentinel/reports interfaceserver sh ./run_tests.sh || true'
        junit 'reports/junit.xml'
        cobertura autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'reports/coverage.xml', conditionalCoverageTargets: '70, 0, 0', failUnhealthy: false, failUnstable: false, lineCoverageTargets: '80, 0, 0', maxNumberOfBuilds: 0, methodCoverageTargets: '80, 0, 0', onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false
      }
    }
    stage('Publish') {
      when {
        branch 'master'
      }
      steps {
        sh 'docker tag seandooher/sentinel-iot:$ID seandooher/sentinel-iot:latest'
        sh 'docker push seandooher/sentinel-iot:latest'
      }
    }
  }
  post {
    always {
      sh 'docker-compose -p $ID down -v'
      sh 'docker container prune -f'
      sh 'docker network prune -f'
     }
  }
}
