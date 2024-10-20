{{/*
Expand the name of the chart.
*/}}
{{- define "cs-ubb-mlops-test-job.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "cs-ubb-mlops-test-job.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "cs-ubb-mlops-test-job.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "cs-ubb-mlops-test-job.labels" -}}
helm.sh/chart: {{ include "cs-ubb-mlops-test-job.chart" . }}
{{ include "cs-ubb-mlops-test-job.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "cs-ubb-mlops-test-job.selectorLabels" -}}
app.kubernetes.io/name: {{ include "cs-ubb-mlops-test-job.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "cs-ubb-mlops-test-job.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "cs-ubb-mlops-test-job.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}


{{/*
Macros for determining the image uri
*/}}
{{- define "image.repository" -}}
  {{- if hasKey .Values "image" -}}
    {{- if hasKey .Values.image "repository" -}}
      {{- .Values.image.repository -}}
    {{- else -}}
      {{- fail "Error: 'image.repository' is required. Please add it to your values.yaml" -}}
    {{- end -}}
  {{- else -}}
    {{- fail "Error: 'image.repository' is required. Please define 'image' object in your values.yaml" -}}
  {{- end -}}
{{- end -}}
{{- define "image.tag" -}}
  {{- if hasKey .Values "image" -}}
    {{- .Values.image.tag | default "main" -}}
  {{- else -}}
    "main"
  {{- end -}}
{{- end -}}
{{- define "image.uri" -}}
{{- printf "%s:%s" (include "image.repository" .) (include "image.tag" .) -}}
{{- end -}}