resource "aws_s3_bucket" "daily-report-s3-bucket" {
  bucket = "sensor-daily-report-bucket"
}

resource "aws_s3_bucket_policy" "daily-report-s3-bucket_bucket_policy" {
  bucket = aws_s3_bucket.daily-report-s3-bucket.id
  policy = data.aws_iam_policy_document.daily-report-s3-bucket_bucket_policy_document.json
}

data "aws_iam_policy_document" "daily-report-s3-bucket_bucket_policy_document" {
  statement {
    principals {
      type        = "Service"
      identifiers = ["timestream.amazonaws.com"]
    }

    actions = [
      "s3:GetBucketLocation",
      "s3:PutObject",
    ]

    resources = [
      aws_s3_bucket.daily-report-s3-bucket.arn,
      "${aws_s3_bucket.daily-report-s3-bucket.arn}/*",
    ]
  }
}