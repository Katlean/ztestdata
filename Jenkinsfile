stdPackageList = []
TWINE_IMAGE = 'zaml-zest-dev.jfrog.io/zamldocker/twine:latest'
TWINE_RUN_ARGS = '--pull=always -v /tmp/tmp_release_passwd:/etc/passwd' // always pull the latest image and mount the passwd file

List<String> findPaths(String root, String path, String type) {
    return sh(returnStdout: true, script: "find $root -not -path '*/.*' -not -path '*/build/*' -type $type -path '$root$path'").trim().split()
}

void publishPackages(String artifactoryUrl, List<String> packageList) {
    // Upload to Artifactory PyPi
    //  use the previously found packageList since we're in a different workspace
    for (packagePath in packageList) {
        String packageFileName = packagePath.split('/')[-1] // PACKAGENAME-0.1.0.tar.gz or PACKAGENAME-0.1.0-py3-none-any.whl
        echo "Publishing $packageFileName package to $artifactoryUrl"
        sh "twine upload --verbose --repository-url $artifactoryUrl -p \"\$ARTIFACTORY_CREDS_PSW\" -u \"\$ARTIFACTORY_CREDS_USR\" ${env.WORKSPACE}${packagePath}"
    }
}

void publishAllPackages() {
    // Publish all packages to Artifactory
    echo 'Publishing packages to Artifactory'
    publishPackages(env.ARTIFACTORY_URL, stdPackageList)
}

List<String> preparePackageList(List<String> packagePathList, String fileExt) {
    // Prepare the package list for publishing
    List<String> preparedPackageList = []

    for (item in packagePathList) {
        String relativePath = item.substring(env.WORKSPACE.length())
        preparedPackageList.add(relativePath)
        String packageFileName = item.split('/')[-1] // PACKAGENAME-0.1.0.tar.gz
        // removes extension and splits by '-' to get the version (whl exmp: PACKAGENAME-0.1.0-py3-none-any.whl, tar.gz exmp: PACKAGENAME-0.1.0.tar.gz)
        String packageVersion = packageFileName.replaceAll(".$fileExt", '') .split('-')[1] // e.g. '0.1.0'
        sh """
            if ! [ "$packageVersion" = "\$PACKAGE_VERSION" ] ; then
                echo "INFO: parsed versions don't match for $packageFileName: $packageVersion != \$PACKAGE_VERSION"
                exit 1
            fi
            env
        """
    }

    return preparedPackageList
}

/*
def trigger_image_build_workflow(String workflowUrl, String imageBuildName, String inputsJsonString) {
    // Triggers an image build GitHub Actions workflow for a given repository
    try {
        def headers = '-H "Accept: application/vnd.github+json" -H "Authorization: Bearer $GITHUB_DEPLOY_ACCESS_TOKEN" -H "X-GitHub-Api-Version: 2022-11-28"'
        def body = "{\"ref\":\"master\",\"inputs\": $inputsJsonString}"
        def response = sh(script: "curl --fail -L -X POST $headers -d \'$body\' $workflowUrl", returnStdout: true).trim()
        echo "Response: ${response}"
    } catch (Exception e) {
        echo "Failed to trigger ${imageBuildName} build: ${e.getMessage()}"
        throw e
    }
}
*/

pipeline {
    agent any
    environment {
        REPONAME = 'ztestdata'
        SOURCE_PATH = 'ztestdata'
        PACKAGE_NAME = 'ztestdata'
        GIT_REPO_URL = "git@github.com:Katlean/${REPONAME}.git"
        ARTIFACTORY_CREDS = credentials('build-push-user-artifactory')
        ARTIFACTORY_PATH = 'zaml.jfrog.io/zaml/api/pypi/zest_pypi'
        ARTIFACTORY_URL = "https://$ARTIFACTORY_PATH"
        PIP_INDEX_URL = "https://$ARTIFACTORY_CREDS_USR:$ARTIFACTORY_CREDS_PSW@$ARTIFACTORY_PATH/simple"
        PACKAGE_VERSION = sh(returnStdout: true, script: "cat $SOURCE_PATH/.VERSION").trim()
        RELEASE_TAG = "v${env.PACKAGE_VERSION}"
        GITHUB_DEPLOY_APP_CREDS = credentials('zest-deploy-configuration-app')
        GITHUB_DEPLOY_ACCESS_TOKEN = "${env.GITHUB_DEPLOY_APP_CREDS_PSW}"
    }
    stages {
        stage('Clean') {
            steps {
                script {
                    // Remove existing virtualenv
                    sh '''
                        rm -rf .venv
                    '''
                    // remove all dist folders
                    List<String> distList = findPaths(env.WORKSPACE, '*/dist', 'd')
                    for (distPath in distList) {
                        sh "rm -rf ${distPath}"
                    }
                }
            }
        }
        stage('Clean (Full)') {
            when {
                anyOf {
                    branch 'release/**'
                    branch 'master'
                }
            }
            steps {
                // only clean the build folder in master and release branches
                //  to allow for faster subsequent builds in non-release branches
                script {
                    // remove all build folders
                    List<String> buildList = findPaths(env.WORKSPACE, '*/build', 'd')
                    for (buildPath in buildList) {
                        sh "rm -rf ${buildPath}"
                    }
                }
            }
        }
        stage('Build and Test') {
            agent {
                docker {
                    image 'python:3.10'
                    reuseNode true
                }
            }
            stages {
                stage('Build') {
                    steps {
                        script {
                            sh '''
                            set -e
                            python -m venv .venv-setup
                            . .venv-setup/bin/activate
                            python -m pip install --upgrade pip setuptools build
                            '''
                            // using --no-isolation on build commands since we are already using a dedicated venv for building
                            // run all setup.py
                            List<String> setupList = findPaths(env.WORKSPACE, '*/setup.py', 'f')
                            for (setup in setupList) {
                                setupDir = setup.substring(0, setup.lastIndexOf('/'))
                                // reactivate venv, switch to setupDir, and build
                                sh """
                                    set -e
                                    . .venv-setup/bin/activate
                                    (cd ${setupDir}; python -m build -s --no-isolation; CYTHONIZE=True SKIP_CLEAN=True python -m build -w --no-isolation)
                                """
                            }

                            stash includes: '**/dist/*.tar.gz', name: 'package'
                        }
                    }
                }
                stage('Install Dependencies') {
                    steps {
                        // Install the built ROOT package (dist/*.tar.gz), then test and report
                        sh '''
                            set -e
                            python -m venv .venv
                            . .venv/bin/activate
                            python -m pip install --upgrade pip setuptools
                            PKG_NAME=$(ls dist/*.tar.gz)
                            pip install --no-cache-dir $PKG_NAME[all,dev]
                        '''
                    }
                }
                stage('Lint') {
                    steps {
                        // lint for ERRORS only
                        sh """
                            . .venv/bin/activate
                            pylint --load-plugins pylint_pydantic -E $SOURCE_PATH --ignore=setup.py
                        """
                    }
                }
                stage('Test') {
                    parallel {
                        stage('Unit-source') {
                            steps {
                                sh """
                                    . .venv/bin/activate
                                    coverage run -m --source=$SOURCE_PATH pytest --color=yes --verbose ./tests/unit
                                    coverage report -mi
                                """
                            }
                        }
                        stage('Integration-source') {
                            steps {
                                sh '''
                                    . .venv/bin/activate
                                    pytest -vv --color=yes tests/integration
                                '''
                            }
                        }
                    }
                }
            }
        }
        stage('Release') {
            when {
                anyOf {
                    branch 'release/**'
                    branch 'master'
                }
            }
            stages {
                stage('Prepare Release') {
                    steps {
                        script {
                            // find all built packages
                            String stdFileExtension = 'tar.gz'

                            List<String> builtstdPackageList = findPaths(env.WORKSPACE, "*/dist/*.$stdFileExtension", 'f')
                            // prepare the package list for publishing
                            echo 'Preparing package list for publishing'
                            stdPackageList = preparePackageList(builtstdPackageList, stdFileExtension)
                        }
                    }
                }
                stage('Release-Setup User') {
                    steps {
                        sh "echo \$(getent passwd \$USER) > /tmp/tmp_release_passwd"
                    }
                }
                stage('Release-Publish (Release Branch) - allow overwrite') {
                    when {
                        anyOf {
                            branch 'release/**'
                        }
                    }
                    agent {
                        docker {
                            image TWINE_IMAGE
                            args TWINE_RUN_ARGS
                            reuseNode true
                        }
                    }
                    steps {
                        script {
                            unstash 'package'
                            publishAllPackages()
                        }
                    }
                }
                stage('Release-Publish (Master Branch) - new versions only') {
                    when {
                        anyOf {
                            branch 'master'
                        }
                    }
                    agent {
                        docker {
                            image TWINE_IMAGE
                            args TWINE_RUN_ARGS
                            reuseNode true
                        }
                    }
                    steps {
                        sshagent(credentials: ['zest-readonly-github-ssh-key']) {
                            script {
                                sh '''
                                    set -e
                                    git remote set-url origin $GIT_REPO_URL
                                    export GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

                                    # remove existing tags causes by saas jenkins issue
                                    git tag -d $(git tag -l)
                                    git fetch --tags
                                    '''

                                if (env.PACKAGE_VERSION.contains('dev')) {
                                    echo 'INFO: Package under development according to the release version. Skip pushing package artifact.'
                                } else {
                                    List<String> gitTags = sh(returnStdout: true, script: 'git tag').trim().split()
                                    if (gitTags.contains(env.RELEASE_TAG)) {
                                        echo 'INFO: Skip pushing package artifact, as version already exists'
                                    } else {
                                        unstash 'package'
                                        publishAllPackages()
                                    }
                                }
                            }
                        }
                    }
                }
                stage('Release-Tag') {
                    steps {
                        sshagent(credentials: ['zest-readonly-github-ssh-key']) {
                            script {
                                env.RELEASED = sh(script: '''
                                    set -e
                                    git remote set-url origin $GIT_REPO_URL
                                    export GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
                                    # remove existing tags causes by saas jenkins issue
                                    git tag -d $(git tag -l)
                                    git fetch --tags

                                    # Skip if version already exists
                                    if ! git tag | grep -E "^$RELEASE_TAG$" ; then
                                        echo "INFO: Tagging and pushing package artifact at new version $RELEASE_TAG"
                                        # Tag commit with version
                                        git tag $RELEASE_TAG && echo "git tag success"
                                        git push --tags && echo "git push success"
                                        RELEASED=True
                                    else
                                        echo "INFO: Skip tagging, as version already exists"
                                        RELEASED=False
                                    fi
                                    echo $RELEASED
                                    ''', returnStdout: true).tokenize().last().trim()
                            }
                        }
                    }
                }
                /*
                stage('Trigger image build workflows') {
                    when {
                        environment name: 'RELEASED', value: 'True'
                    }
                    steps {
                        script {
                            def workflow_input = "{\"trigger_reason\":\"$REPONAME $RELEASE_TAG released\"}"
                            // Trigger model-archive-etl image build workflow
                            trigger_image_build_workflow(
                                'https://api.github.com/repos/Katlean/model-archive-etl/actions/workflows/build-and-push-nonprod-etl-image.yml/dispatches',
                                'model-archive-etl',
                                workflow_input
                            )
                        }
                    }
                }
                */
            }
        }
    }
}
