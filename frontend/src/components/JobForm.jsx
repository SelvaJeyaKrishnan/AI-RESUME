import { useState } from 'react'
import toast from 'react-hot-toast'
import { createJob, updateJob } from '../services/api.js'
import { Spinner } from './Loaders.jsx'

export default function JobForm({ job, onSaved, onCancel }) {
  const [title, setTitle] = useState(job?.title || '')
  const [description, setDescription] = useState(job?.description_raw || '')
  const [saving, setSaving] = useState(false)

  const onSubmit = async (e) => {
    e.preventDefault()
    if (description.trim().length < 20) {
      toast.error('Paste a full job description (at least 20 characters)')
      return
    }
    setSaving(true)
    try {
      const payload = { title: title || undefined, description_raw: description }
      const { data } = job ? await updateJob(job.id, payload) : await createJob(payload)
      toast.success(job ? 'Job updated' : 'Job created — requirements extracted automatically')
      onSaved?.(data)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Could not save the job')
    } finally {
      setSaving(false)
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div>
        <label className="text-sm font-medium mb-1 block">Job title (optional)</label>
        <input
          className="input"
          placeholder="We'll detect one from the description if left blank"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
      </div>
      <div>
        <label className="text-sm font-medium mb-1 block">Job description</label>
        <textarea
          className="input font-mono text-xs leading-relaxed"
          rows={14}
          required
          placeholder="Paste the full job description here — required skills, preferred skills, experience, education, and responsibilities will be extracted automatically."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>
      <div className="flex justify-end gap-2 pt-2">
        <button type="button" className="btn-secondary" onClick={onCancel}>Cancel</button>
        <button type="submit" className="btn-primary" disabled={saving}>
          {saving && <Spinner className="h-4 w-4" />}
          {job ? 'Save changes' : 'Create job'}
        </button>
      </div>
    </form>
  )
}
