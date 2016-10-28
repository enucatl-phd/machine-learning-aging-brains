require "time"
now = Time.now.to_i
user = ENV["USER"]
id = "#{user}-#{now}"
project = "machine-learning-aging-brains"
bucket = "gs://mlp1-data-high-avail"

output = "#{bucket}/output/output-#{id}"
jobname = "#{project}-#{id}"

namespace :run do

  desc "run on the cloud with a slice of the data and only two test files"
  task :cloud_smaller do
    sh [
      "python main.py",
      "--project #{project}",
      "--job_name #{jobname}",
      "--runner BlockingDataflowPipelineRunner",
      "--max_num_workers 24",
      "--autoscaling_algorithm THROUGHPUT_BASED",
      "--staging_location #{bucket}/staging",
      "--temp_location #{bucket}/temp",
      "--output #{output}",
      "--zone europe-west1-c",
      "--disk_size_gb 15",
      "--worker_machine_type n1-highcpu-2",
      "--setup_file ./setup.py",
      "--test_slice",
      "--ages #{bucket}/targets.csv",
      "--train \"#{bucket}/set_train/train_*.nii\"",
      "--test \"#{bucket}/set_test/test_1[01].nii\""
    ].join(" ")
  end

  desc "run on the cloud the full dataset"
  task :cloud_big do
    sh [
      "python main.py",
      "--project #{project}",
      "--job_name #{jobname}",
      "--runner DataflowPipelineRunner",
      "--max_num_workers 24",
      "--autoscaling_algorithm THROUGHPUT_BASED",
      "--staging_location #{bucket}/staging",
      "--temp_location #{bucket}/temp",
      "--output #{output}",
      "--zone europe-west1-c",
      "--disk_size_gb 15",
      "--worker_machine_type n1-highcpu-2",
      "--setup_file ./setup.py",
      "--ages #{bucket}/targets.csv",
      "--train \"#{bucket}/set_train/train_*.nii\"",
      "--test \"#{bucket}/set_test/test_*.nii\"",
    ].join(" ")
  end

  desc "run on the cloud with all test files, but only a slice of the data"
  task :cloud_small do
    sh [
      "python main.py",
      "--project #{project}",
      "--job_name #{jobname}",
      "--runner BlockingDataflowPipelineRunner",
      "--max_num_workers 24",
      "--autoscaling_algorithm THROUGHPUT_BASED",
      "--staging_location #{bucket}/staging",
      "--temp_location #{bucket}/temp",
      "--output #{output}",
      "--zone europe-west1-c",
      "--disk_size_gb 15",
      "--worker_machine_type n1-highcpu-2",
      "--setup_file ./setup.py",
      "--test_slice",
      "--ages #{bucket}/targets.csv",
      "--train \"#{bucket}/set_train/train_*.nii\"",
      "--test \"#{bucket}/set_test/test_*.nii\"",
    ].join(" ")
  end

  desc "run locally with two files only"
  task :local_small do
    sh [
      "python main.py",
      "--test_slice"
    ].join(" ")
  end

  desc "run locally with all files"
  task :local_big do
    sh [
      "python main.py",
      "--test_slice",
      "--train \"data/set_train/train_*.nii\"",
    ].join(" ")
  end


  desc "ls output from the cloud"
  task :ls do
    sh "gsutil ls #{bucket}/output/"
  end
end
