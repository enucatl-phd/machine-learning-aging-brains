project = "machine-learning-aging-brains"
bucket = "gs://mlp1-data"

namespace :run do

  desc "run async on the cloud"
  task :cloud do
    sh [
      "python main.py",
      "--project #{project}",
      "--job_name #{project}-main1",
      "--runner DataflowPipelineRunner",
      "--max_num_workers 300",
      "--autoscaling_algorithm THROUGHPUT_BASED",
      "--staging_location #{bucket}/staging",
      "--temp_location #{bucket}/temp",
      "--output #{bucket}/output/output",
      "--zone europe-west1-c",
      "--setup_file ./setup.py",
      "--ages #{bucket}/targets.csv",
      "--input \"#{bucket}/set_train/train_*.nii\""
    ].join(" ")
  end

  desc "run on the cloud"
  task :cloud_blocking do
    sh [
      "python main.py",
      "--project #{project}",
      "--job_name #{project}-main1",
      "--runner BlockingDataflowPipelineRunner",
      "--staging_location #{bucket}/staging",
      "--temp_location #{bucket}/temp",
      "--output #{bucket}/output/output",
      "--zone europe-west1-c",
      "--setup_file ./setup.py",
      "--ages #{bucket}/targets.csv",
      "--input \"#{bucket}/set_train/train_*.nii\""
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
      "--input \"data/set_train/train_*.nii\"",
    ].join(" ")
  end


  desc "copy output from the cloud"
  task :copy do
    sh "gsutil cp \"#{bucket}/output/*\" output"
  end
end
