pipeline {
    agent {
        node {
            label 'generic-agent'
        }
    }
    stages {
          stage('Check Dev Website') {
            steps {
                script {
                    sh """
                    curl "https://${c368pratyushak}}dev.computerlab.online/"
                    """
                }
            }
        }
    }
}
