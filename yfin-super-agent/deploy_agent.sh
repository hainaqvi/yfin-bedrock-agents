#!/bin/bash

# Exit on any error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

print_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

print_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}"
}

# Check if AWS CLI is installed
check_aws_cli() {
    print_status "Checking AWS CLI installation..."
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    print_success "AWS CLI is installed"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install it first."
        exit 1
    fi
    print_success "Python 3 is installed"
}

# Check AWS credentials
check_aws_credentials() {
    print_status "Checking AWS credentials..."
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    print_success "AWS credentials verified"
}

# Setup Python virtual environment
setup_venv() {
    print_status "Setting up Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Install required packages
install_requirements() {
    print_status "Installing required packages..."
    pip install boto3
    print_success "Packages installed"
}

# Run the agent creation script
run_agent_creation() {
    print_status "Running Bedrock agent creation script..."
    python3 yfin-super-agent/src/create_agent.py
    if [ $? -eq 0 ]; then
        print_success "Agent creation completed successfully"
    else
        print_error "Agent creation failed"
        exit 1
    fi
}

# Main execution
main() {
    print_status "Starting Bedrock agent deployment..."
    
    # Run checks
    check_aws_cli
    check_python
    check_aws_credentials
    
    # Setup environment
    install_requirements
    
    # Run agent creation
    run_agent_creation
    
    print_success "Deployment completed successfully"
}

# Run main function
main
