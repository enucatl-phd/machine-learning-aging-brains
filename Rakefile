require "time"
now = Time.now.to_i
user = ENV["USER"]
id = "#{user}-#{now}"
project = "machine-learning-aging-brains"
bucket = "gs://mlp1-data-high-avail"

output = "#{bucket}/output/output-#{id}"
jobname = "#{project}-#{id}"

namespace :correlation do

  output = "#{bucket}/correlation_output/output-#{id}"
  desc "calculate the correlation on the cloud with a slice of the data and only two test files"
  task :cloud_smaller do
    sh [
      "python correlation.py",
      "--project #{project}",
      "--job_name #{jobname}",
      "--runner BlockingDataflowPipelineRunner",
      "--max_num_workers 24",
      "--autoscaling_algorithm THROUGHPUT_BASED",
      "--staging_location #{bucket}/staging",
      "--temp_location #{bucket}/temp",
      "--output #{output}",
      "--zone europe-west1-c",
      "--disk_size_gb 100",
      "--worker_machine_type n1-highcpu-2",
      "--setup_file ./setup.py",
      "--test_slice",
      "--ages #{bucket}/targets.csv",
      "--input \"#{bucket}/set_train/train_*.nii\"",
    ].join(" ")
  end

  desc "calculate the correlation on the cloud the full dataset"
  task :cloud_big do
    sh [
      "python correlation.py",
      "--project #{project}",
      "--job_name #{jobname}",
      "--runner DataflowPipelineRunner",
      "--max_num_workers 24",
      "--autoscaling_algorithm THROUGHPUT_BASED",
      "--staging_location #{bucket}/staging",
      "--temp_location #{bucket}/temp",
      "--output #{output}",
      "--zone europe-west1-c",
      "--disk_size_gb 100",
      "--worker_machine_type n1-highcpu-2",
      "--setup_file ./setup.py",
      "--ages #{bucket}/targets.csv",
      "--input \"#{bucket}/set_train/train_*.nii\"",
    ].join(" ")
  end

  desc "calculate the correlation on the cloud with all test files, but only a slice of the data"
  task :cloud_small do
    sh [
      "python correlation.py",
      "--project #{project}",
      "--job_name #{jobname}",
      "--runner BlockingDataflowPipelineRunner",
      "--max_num_workers 24",
      "--autoscaling_algorithm THROUGHPUT_BASED",
      "--staging_location #{bucket}/staging",
      "--temp_location #{bucket}/temp",
      "--output #{output}",
      "--zone europe-west1-c",
      "--disk_size_gb 100",
      "--worker_machine_type n1-highcpu-2",
      "--setup_file ./setup.py",
      "--test_slice",
      "--ages #{bucket}/targets.csv",
      "--input \"#{bucket}/set_train/train_*.nii\"",
    ].join(" ")
  end

  desc "calculate the correlation locally with two files only"
  task :local_small do
    sh [
      "python correlation.py",
      "--test_slice"
    ].join(" ")
  end

  desc "calculate the correlation locally with all files"
  task :local_big do
    sh [
      "python correlation.py",
      "--test_slice",
      "--train \"data/set_train/train_*.nii\"",
    ].join(" ")
  end

end


namespace :probabilities do

  output = "#{bucket}/prediction_output/output-#{id}"
  desc "calculate the prediction locally with all files"
  task :local do
    sh [
      "python probabilities.py",
      "--test_slice",
    ].join(" ")
  end

  desc "calculate the probabilities on the cloud the full dataset"
  task :cloud do
    sh [
      "python probabilities.py",
      "--project #{project}",
      "--job_name #{jobname}",
      "--runner DataflowPipelineRunner",
      "--max_num_workers 24",
      "--autoscaling_algorithm THROUGHPUT_BASED",
      "--staging_location #{bucket}/staging",
      "--temp_location #{bucket}/temp",
      "--output #{output}",
      "--zone europe-west1-c",
      "--disk_size_gb 100",
      "--worker_machine_type n1-highcpu-2",
      "--setup_file ./setup.py",
      "--ages #{bucket}/targets.csv",
      "--train \"#{bucket}/filtered_set_train/train_*.npy\"",
      "--test \"#{bucket}/filtered_set_test/test_*.npy\"",
    ].join(" ")
  end


end

namespace :cloud do
  desc "ls output from the cloud"
  task :ls do
    sh "gsutil ls #{bucket}/output/"
  end
end
