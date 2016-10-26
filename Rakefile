project = "machine-learning-aging-brains"
bucket = "gs://mlp1-data"

namespace :run do

  desc "run on the cloud"
  task :cloud do
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
    sh "gsutil cp \"#{bucket}/output/*\" output"
  end

end
