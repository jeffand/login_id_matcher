#!/usr/bin/env python3

import boto3
import botocore.session
from botocore.stub import Stubber
from botocore.exceptions import ClientError
import time
from datetime import datetime, timedelta
import json

def simulate_capacity_reservation(params):
    """
    Simulate capacity reservation with retry logic using botocore Stubber.
    
    Args:
        params (dict): Parameters for the capacity reservation
        
    Returns:
        dict: Results of the simulation including success/failure and metrics
    """
    # Create a new session and client with stubber
    session = botocore.session.Session()
    ec2 = session.create_client('ec2')
    stubber = Stubber(ec2)
    
    # Convert parameters
    max_duration = int(params['MaxRetryDurationMinutes']) * 60
    initial_interval = int(params['InitialRetryIntervalSeconds'])
    max_interval = int(params['MaxRetryIntervalSeconds'])
    backoff = float(params['BackoffMultiplier'])
    
    # Prepare the expected successful response
    success_response = {
        'CapacityReservation': {
            'CapacityReservationId': 'cr-test-123456789',
            'OwnerId': '123456789012',
            'CapacityReservationArn': 'arn:aws:ec2:region:123456789012:capacity-reservation/cr-test-123456789',
            'InstanceType': params['InstanceType'],
            'InstancePlatform': params['Platform'],
            'AvailabilityZone': params['AvailabilityZone'],
            'Tenancy': params['Tenancy'],
            'TotalInstanceCount': 1,
            'AvailableInstanceCount': 1,
            'EbsOptimized': True,
            'EphemeralStorage': False,
            'State': 'active',
            'EndDate': None,
            'EndDateType': 'unlimited',
            'InstanceMatchCriteria': 'targeted',
            'CreateDate': datetime.now().isoformat(),
            'Tags': []
        }
    }
    
    # Prepare the expected error response
    error_response = {
        'Error': {
            'Code': 'InsufficientInstanceCapacity',
            'Message': 'We currently do not have sufficient capacity in the Availability Zone you requested'
        }
    }
    
    # Configure the stubber for multiple attempts
    start_time = datetime.now()
    current_interval = initial_interval
    attempt = 1
    
    # Simulate a series of failed attempts followed by success
    while (datetime.now() - start_time).total_seconds() < max_duration:
        # Simulate failure for the first 3 attempts
        if attempt <= 3:
            stubber.add_client_error(
                'create_capacity_reservation',
                service_error_code='InsufficientInstanceCapacity',
                service_message='Simulated capacity not available',
                expected_params={
                    'InstanceType': params['InstanceType'],
                    'InstancePlatform': params['Platform'],
                    'AvailabilityZone': params['AvailabilityZone'],
                    'InstanceCount': 1,
                    'InstanceMatchCriteria': 'targeted',
                    'Tenancy': params['Tenancy'],
                    'EndDateType': 'unlimited'
                }
            )
        else:
            # Simulate success on the 4th attempt
            stubber.add_response(
                'create_capacity_reservation',
                success_response,
                {
                    'InstanceType': params['InstanceType'],
                    'InstancePlatform': params['Platform'],
                    'AvailabilityZone': params['AvailabilityZone'],
                    'InstanceCount': 1,
                    'InstanceMatchCriteria': 'targeted',
                    'Tenancy': params['Tenancy'],
                    'EndDateType': 'unlimited'
                }
            )
        
        try:
            with stubber:
                response = ec2.create_capacity_reservation(
                    InstanceType=params['InstanceType'],
                    InstancePlatform=params['Platform'],
                    AvailabilityZone=params['AvailabilityZone'],
                    InstanceCount=1,
                    InstanceMatchCriteria='targeted',
                    Tenancy=params['Tenancy'],
                    EndDateType='unlimited'
                )
                
                # If we get here, the request succeeded
                duration = int((datetime.now() - start_time).total_seconds())
                return {
                    'success': True,
                    'capacityReservationId': response['CapacityReservation']['CapacityReservationId'],
                    'attempts': attempt,
                    'totalDuration': duration,
                    'finalInterval': current_interval
                }
                
        except ClientError as e:
            # Calculate remaining time
            elapsed = (datetime.now() - start_time).total_seconds()
            remaining = max_duration - elapsed
            
            if remaining < current_interval:
                return {
                    'success': False,
                    'error': f'InsufficientCapacity after {attempt} attempts over {int(elapsed)} seconds',
                    'attempts': attempt,
                    'totalDuration': int(elapsed),
                    'finalInterval': current_interval
                }
            
            # Simulate the wait between retries
            print(f"Attempt {attempt} failed, waiting {current_interval} seconds...")
            time.sleep(0.1)  # Minimal sleep for simulation
            
            # Update for next attempt
            current_interval = min(current_interval * backoff, max_interval)
            attempt += 1
            
    # If we get here, we exceeded the maximum duration
    return {
        'success': False,
        'error': f'Exceeded maximum retry duration ({max_duration} seconds) after {attempt} attempts',
        'attempts': attempt,
        'totalDuration': max_duration,
        'finalInterval': current_interval
    }

def test_simulation():
    """Run a test simulation with sample parameters"""
    test_params = {
        'InstanceType': 'm5.xlarge',
        'Platform': 'Linux/UNIX',
        'AvailabilityZone': 'us-east-1a',
        'Tenancy': 'default',
        'MaxRetryDurationMinutes': '60',
        'InitialRetryIntervalSeconds': '30',
        'MaxRetryIntervalSeconds': '300',
        'BackoffMultiplier': '2'
    }
    
    print("Starting capacity reservation simulation...")
    result = simulate_capacity_reservation(test_params)
    print("\nSimulation Results:")
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    test_simulation()
