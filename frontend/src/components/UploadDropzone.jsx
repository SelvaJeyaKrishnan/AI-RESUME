import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { UploadCloud } from 'lucide-react'
import toast from 'react-hot-toast'
import { uploadResumes } from '../services/api.js'
import { Spinner } from './Loaders.jsx'

const ACCEPTED = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'text/plain': ['.txt'],
}

export default function UploadDropzone({ onUploaded }) {
  const [uploading, setUploading] = useState(false)

  const onDrop = useCallback(
    async (accepted, rejected) => {
      if (rejected?.length) {
        rejected.forEach((r) => toast.error(`${r.file.name}: unsupported file type or too large`))
      }
      if (!accepted.length) return

      setUploading(true)
      try {
        const { data } = await uploadResumes(accepted)
        const succeeded = data.filter((r) => r.resume.parse_status === 'success').length
        const failed = data.length - succeeded
        if (succeeded) toast.success(`Parsed ${succeeded} resume${succeeded === 1 ? '' : 's'} successfully`)
        if (failed) toast.error(`${failed} resume${failed === 1 ? '' : 's'} failed to parse`)
        onUploaded?.(data)
      } catch (err) {
        toast.error(err.response?.data?.detail || 'Upload failed')
      } finally {
        setUploading(false)
      }
    },
    [onUploaded]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED,
    maxSize: 10 * 1024 * 1024,
    multiple: true,
  })

  return (
    <div
      {...getRootProps()}
      className={`rounded-md border-2 border-dashed px-6 py-10 text-center cursor-pointer transition-colors ${
        isDragActive
          ? 'border-brand-500 bg-brand-50 dark:bg-brand-500/10'
          : 'border-line dark:border-lineDark hover:border-brand-300'
      }`}
    >
      <input {...getInputProps()} />
      {uploading ? (
        <div className="flex flex-col items-center gap-2 text-ink/60 dark:text-paper/60">
          <Spinner className="h-6 w-6" />
          <p className="text-sm">Parsing resumes…</p>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-2">
          <UploadCloud className="h-7 w-7 text-ink/40 dark:text-paper/40" strokeWidth={1.5} />
          <p className="text-sm font-medium">
            {isDragActive ? 'Drop resumes here' : 'Drag and drop resumes, or click to browse'}
          </p>
          <p className="text-xs text-ink/40 dark:text-paper/40">PDF, DOCX or TXT — up to 10MB each</p>
        </div>
      )}
    </div>
  )
}
