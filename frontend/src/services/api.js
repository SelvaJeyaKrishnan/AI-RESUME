import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export const api = axios.create({ baseURL: BASE_URL })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('resumeai_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('resumeai_token')
      localStorage.removeItem('resumeai_user')
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// ---- Auth ----
export const registerUser = (payload) => api.post('/auth/register', payload)
export const loginUser = (payload) => api.post('/auth/login', payload)
export const getMe = () => api.get('/auth/me')

// ---- Jobs ----
export const listJobs = () => api.get('/jobs')
export const getJob = (jobId) => api.get(`/jobs/${jobId}`)
export const createJob = (payload) => api.post('/jobs', payload)
export const updateJob = (jobId, payload) => api.put(`/jobs/${jobId}`, payload)
export const deleteJob = (jobId) => api.delete(`/jobs/${jobId}`)

// ---- Resumes ----
export const listResumes = () => api.get('/resumes')
export const getResume = (resumeId) => api.get(`/resumes/${resumeId}`)
export const uploadResumes = (files, onProgress) => {
  const form = new FormData()
  files.forEach((f) => form.append('files', f))
  return api.post('/resumes/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: onProgress,
  })
}
export const deleteResume = (resumeId) => api.delete(`/resumes/${resumeId}`)
export const reprocessResume = (resumeId) => api.post(`/resumes/${resumeId}/reprocess`)
export const downloadResumeUrl = (resumeId) => `${BASE_URL}/resumes/${resumeId}/download`

// ---- Analysis ----
export const analyzeResume = (resumeId, jobId) => api.post(`/analysis/${resumeId}/${jobId}`)
export const getAnalysis = (resumeId, jobId) => api.get(`/analysis/${resumeId}/${jobId}`)
export const getJobCandidates = (jobId) => api.get(`/jobs/${jobId}/candidates`)
export const getJobRanking = (jobId) => api.get(`/jobs/${jobId}/ranking`)
export const compareCandidates = (jobId, resumeIds) =>
  api.post(`/jobs/${jobId}/compare`, { resume_ids: resumeIds })
export const getJobAnalytics = (jobId) => api.get(`/jobs/${jobId}/analytics`)

// ---- Career reports (candidate-facing flow) ----
export const createCareerReport = (file, jobDescription, jobTitle, onProgress) => {
  const form = new FormData()
  form.append('file', file)
  form.append('job_description', jobDescription)
  if (jobTitle) form.append('job_title', jobTitle)
  return api.post('/career/reports', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: onProgress,
  })
}
export const getCareerAssessment = (reportId) => api.get(`/career/reports/${reportId}/assessment`)
export const submitAssessmentAnswer = (reportId, questionId, optionId) =>
  api.post(`/career/reports/${reportId}/assessment/answer`, {
    question_id: questionId,
    option_id: optionId,
  })
export const completeAssessment = (reportId) =>
  api.post(`/career/reports/${reportId}/assessment/complete`)
export const getCareerReport = (reportId) => api.get(`/career/reports/${reportId}`)
export const listCareerReports = () => api.get('/career/reports')
export const deleteCareerReport = (reportId) => api.delete(`/career/reports/${reportId}`)
