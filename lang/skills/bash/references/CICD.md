# CI/CD Integration for Bash Scripts

Comprehensive guide to integrating Bash scripts into CI/CD pipelines with automated testing, security scanning, and deployment.

## GitHub Actions

### Basic Workflow

```yaml
name: Shell Script CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Install ShellCheck
        run: sudo apt-get update && sudo apt-get install -y shellcheck

      - name: Install shfmt
        run: |
          GO111MODULE=on go install mvdan.cc/sh/v3/cmd/shfmt@latest
          echo "$HOME/go/bin" >> $GITHUB_PATH

      - name: Install bats
        run: sudo apt-get install -y bats

      - name: Run ShellCheck
        run: shellcheck --enable=all *.sh

      - name: Check formatting
        run: shfmt -d -i 2 -ci -bn -sr -kp *.sh

      - name: Run tests
        run: bats test/
```

### Matrix Testing (Multiple Bash Versions)

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        bash-version: ['4.4', '5.0', '5.1', '5.2']

    steps:
      - uses: actions/checkout@v3

      - name: Setup Bash ${{ matrix.bash-version }}
        run: |
          docker pull bash:${{ matrix.bash-version }}

      - name: Run tests in container
        run: |
          docker run --rm \
            -v "$PWD:/work" \
            -w /work \
            bash:${{ matrix.bash-version }} \
            bats test/
```

### Security Scanning

```yaml
jobs:
  security:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Run Trivy scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Scan for secrets
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
```

### Coverage Reporting

```yaml
jobs:
  coverage:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Install kcov
        run: |
          sudo apt-get update
          sudo apt-get install -y kcov bats

      - name: Run tests with coverage
        run: |
          kcov --exclude-pattern=/usr coverage/ bats test/

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          directory: ./coverage
          flags: bash
          name: bash-coverage

      - name: Generate coverage badge
        run: |
          COVERAGE=$(grep -oP '(?<=<span class="headerCovTableEntryLo">)[^<]+' coverage/index.html | head -1)
          echo "Coverage: $COVERAGE"
```

### Automated Releases

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Create Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false

      - name: Build artifacts
        run: |
          mkdir -p dist
          tar -czf dist/scripts.tar.gz *.sh lib/

      - name: Upload Release Asset
        uses: actions/upload-release-asset@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          upload_url: ${{ steps.create_release.outputs.upload_url }}
          asset_path: ./dist/scripts.tar.gz
          asset_name: scripts.tar.gz
          asset_content_type: application/gzip
```

## GitLab CI/CD

### Basic Pipeline

```yaml
# .gitlab-ci.yml

stages:
  - lint
  - test
  - security
  - deploy

shellcheck:
  stage: lint
  image: koalaman/shellcheck-alpine
  script:
    - shellcheck --enable=all *.sh
  only:
    - merge_requests
    - main

shfmt:
  stage: lint
  image: mvdan/shfmt
  script:
    - shfmt -d -i 2 -ci -bn -sr -kp *.sh
  only:
    - merge_requests
    - main

bats-test:
  stage: test
  image: bash:5.2
  before_script:
    - apk add --no-cache bats
  script:
    - bats test/
  coverage: '/^Covered: (\d+\.\d+)%/'
  artifacts:
    reports:
      junit: test-results.xml

security-scan:
  stage: security
  image: aquasec/trivy
  script:
    - trivy fs --security-checks vuln,config .
  only:
    - main

deploy:
  stage: deploy
  image: bash:5.2
  script:
    - ./deploy.sh
  only:
    - main
  when: manual
```

### Matrix Testing in GitLab

```yaml
.test-template:
  stage: test
  script:
    - bats test/

test:bash-4.4:
  extends: .test-template
  image: bash:4.4

test:bash-5.0:
  extends: .test-template
  image: bash:5.0

test:bash-5.2:
  extends: .test-template
  image: bash:5.2
```

## Pre-commit Hooks

### Configuration

```yaml
# .pre-commit-config.yaml

repos:
  - repo: https://github.com/shellcheck-py/shellcheck-py
    rev: v0.9.0.6
    hooks:
      - id: shellcheck
        args: ['--enable=all', '--exclude=SC2312']

  - repo: https://github.com/scop/pre-commit-shfmt
    rev: v3.7.0-1
    hooks:
      - id: shfmt
        args: ['-i', '2', '-ci', '-bn', '-sr', '-kp', '-w']

  - repo: https://github.com/openstack/bashate
    rev: 2.1.1
    hooks:
      - id: bashate
        args: ['--ignore=E006']

  - repo: local
    hooks:
      - id: bats-test
        name: Run bats tests
        entry: bats
        args: ['test/']
        language: system
        pass_filenames: false

      - id: check-bash-version
        name: Check minimum Bash version
        entry: bash
        args: ['-c', 'grep -q "BASH_VERSINFO" *.sh']
        language: system
        pass_filenames: false
```

### Installation

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Custom Hook Script

```bash
#!/bin/bash
# .git/hooks/pre-commit

set -e

# Run ShellCheck
echo "Running ShellCheck..."
shellcheck --enable=all *.sh

# Run shfmt
echo "Checking formatting..."
shfmt -d -i 2 -ci -bn -sr -kp *.sh

# Run tests
echo "Running tests..."
bats test/

echo "All checks passed!"
```

## Jenkins

### Declarative Pipeline

```groovy
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Lint') {
            parallel {
                stage('ShellCheck') {
                    steps {
                        sh 'shellcheck --enable=all *.sh'
                    }
                }
                stage('shfmt') {
                    steps {
                        sh 'shfmt -d -i 2 -ci -bn -sr -kp *.sh'
                    }
                }
            }
        }

        stage('Test') {
            steps {
                sh 'bats test/'
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('Security Scan') {
            steps {
                sh 'trivy fs --security-checks vuln,config .'
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh './deploy.sh'
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
```

## CircleCI

### Configuration

```yaml
# .circleci/config.yml

version: 2.1

jobs:
  lint:
    docker:
      - image: koalaman/shellcheck-alpine
    steps:
      - checkout
      - run:
          name: ShellCheck
          command: shellcheck --enable=all *.sh

  test:
    docker:
      - image: bash:5.2
    steps:
      - checkout
      - run:
          name: Install bats
          command: apk add --no-cache bats
      - run:
          name: Run tests
          command: bats test/
      - store_test_results:
          path: test-results

workflows:
  version: 2
  lint-and-test:
    jobs:
      - lint
      - test:
          requires:
            - lint
```

## Travis CI

### Configuration

```yaml
# .travis.yml

language: bash

os:
  - linux
  - osx

env:
  - BASH_VERSION=4.4
  - BASH_VERSION=5.2

install:
  - if [[ "$TRAVIS_OS_NAME" == "linux" ]]; then sudo apt-get install -y shellcheck bats; fi
  - if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then brew install shellcheck bats-core; fi

script:
  - shellcheck --enable=all *.sh
  - shfmt -d -i 2 -ci -bn -sr -kp *.sh
  - bats test/

after_success:
  - bash <(curl -s https://codecov.io/bash)
```

## Docker-Based CI

### Makefile for Local Testing

```makefile
.PHONY: lint test security all

SHELLCHECK := docker run --rm -v "$PWD:/mnt" koalaman/shellcheck-alpine
SHFMT := docker run --rm -v "$PWD:/work" -w /work mvdan/shfmt
BATS := docker run --rm -v "$PWD:/work" -w /work bash:5.2 bats
TRIVY := docker run --rm -v "$PWD:/work" -w /work aquasec/trivy

lint:
	$(SHELLCHECK) shellcheck --enable=all /mnt/*.sh
	$(SHFMT) -d -i 2 -ci -bn -sr -kp .

test:
	$(BATS) test/

security:
	$(TRIVY) fs --security-checks vuln,config .

all: lint test security

# CI-specific target
ci: all
	@echo "All CI checks passed!"
```

### Usage

```bash
# Run locally (same as CI)
make ci

# Run individual checks
make lint
make test
make security
```

## Continuous Deployment

### Deployment Script

```bash
#!/bin/bash
# deploy.sh

set -Eeuo pipefail

readonly DEPLOY_USER="${DEPLOY_USER:?not set}"
readonly DEPLOY_HOST="${DEPLOY_HOST:?not set}"
readonly DEPLOY_PATH="${DEPLOY_PATH:?not set}"

log_info() {
  echo "[INFO] $*" >&2
}

# Deploy to remote server
deploy_to_server() {
  log_info "Deploying to $DEPLOY_HOST..."

  # Copy scripts
  rsync -avz \
    --exclude='.git' \
    --exclude='test/' \
    ./ "$DEPLOY_USER@$DEPLOY_HOST:$DEPLOY_PATH/"

  # Run post-deploy tasks
  ssh "$DEPLOY_USER@$DEPLOY_HOST" bash <<'EOF'
cd /path/to/scripts
chmod +x *.sh
./post-deploy.sh
EOF

  log_info "Deployment completed"
}

# Main
main() {
  deploy_to_server
}

main "$@"
```

### GitHub Action for Deployment

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.DEPLOY_SSH_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -H ${{ secrets.DEPLOY_HOST }} >> ~/.ssh/known_hosts

      - name: Deploy
        env:
          DEPLOY_USER: ${{ secrets.DEPLOY_USER }}
          DEPLOY_HOST: ${{ secrets.DEPLOY_HOST }}
          DEPLOY_PATH: ${{ secrets.DEPLOY_PATH }}
        run: ./deploy.sh
```

## Best Practices

### 1. Fast Feedback

```yaml
# Run quick checks first, slow checks later
jobs:
  quick-lint:
    runs-on: ubuntu-latest
    steps:
      - run: shellcheck *.sh  # Fast

  full-test:
    needs: quick-lint
    runs-on: ubuntu-latest
    steps:
      - run: bats test/  # Slower
```

### 2. Caching

```yaml
- name: Cache dependencies
  uses: actions/cache@v3
  with:
    path: |
      ~/.cache/shellcheck
      ~/go/bin
    key: ${{ runner.os }}-tools-${{ hashFiles('**/*.sh') }}
```

### 3. Fail Fast

```yaml
strategy:
  fail-fast: true  # Stop on first failure
  matrix:
    bash-version: ['4.4', '5.0', '5.2']
```

### 4. Artifact Preservation

```yaml
- name: Upload test results
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: test-results
    path: test-results/
    retention-days: 30
```

## Troubleshooting CI/CD

### Issue: Tests pass locally but fail in CI

**Solution:**
```yaml
# Debug CI environment
- name: Debug environment
  run: |
    echo "Bash version: $BASH_VERSION"
    echo "PATH: $PATH"
    env | sort
    which bash shellcheck bats
```

### Issue: Slow CI builds

**Solution:**
```yaml
# Use Docker layer caching
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v2

- name: Cache Docker layers
  uses: actions/cache@v3
  with:
    path: /tmp/.buildx-cache
    key: ${{ runner.os }}-buildx-${{ github.sha }}
```

### Issue: Flaky tests

**Solution:**
```bash
# Add retry logic to tests
@test "flaky operation" {
  local retries=3
  local count=0

  until run_operation; do
    count=$((count + 1))
    if [ $count -ge $retries ]; then
      fail "Operation failed after $retries attempts"
    fi
    sleep 1
  done
}
```

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [CircleCI Documentation](https://circleci.com/docs/)
