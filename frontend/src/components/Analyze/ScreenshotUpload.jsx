import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Camera, X, Upload, AlertCircle } from 'lucide-react'
import api from '../../hooks/useApi'

function ScreenshotUpload({ platform = 'instagram', onResult }) {
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState(null)

  const onDrop = useCallback((acceptedFiles) => {
    const newFiles = acceptedFiles.map((file) => ({
      file,
      preview: URL.createObjectURL(file),
      id: Math.random().toString(36).slice(2),
    }))
    setFiles((prev) => [...prev, ...newFiles])
    setError(null)
  }, [])

  const removeFile = (id) => {
    setFiles((prev) => prev.filter((f) => f.id !== id))
  }

  const handleUpload = async () => {
    if (files.length === 0) return
    setUploading(true)
    setError(null)
    setProgress(0)

    try {
      const formData = new FormData()
      formData.append('file', files[0].file)
      formData.append('platform', platform)

      const res = await api.post('/api/influencers/screenshot', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => {
          if (e.total) setProgress(Math.round((e.loaded / e.total) * 100))
        },
      })

      onResult?.(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de l\'upload')
    } finally {
      setUploading(false)
      setProgress(0)
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.webp'] },
    maxFiles: 1,
    disabled: uploading,
  })

  return (
    <div className="space-y-4">
      {/* Drop zone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl min-h-[160px] flex flex-col items-center justify-center cursor-pointer transition-all duration-200 ${
          isDragActive
            ? 'border-[#6366F1] bg-[#6366F1]/5'
            : 'border-[#27272A] hover:border-[#3F3F46]'
        } ${uploading ? 'opacity-50 pointer-events-none' : ''}`}
      >
        <input {...getInputProps()} capture="environment" />
        <div className="flex flex-col items-center gap-3 px-4 text-center">
          <div className="w-14 h-14 rounded-xl bg-[#27272A] flex items-center justify-center">
            <Camera className={`w-6 h-6 ${isDragActive ? 'text-[#6366F1]' : 'text-[#71717A]'}`} />
          </div>
          <div>
            <p className="text-sm text-[#FAFAFA] font-medium">
              {isDragActive ? 'Deposez l\'image ici...' : 'Appuyez pour prendre une photo'}
            </p>
            <p className="text-xs text-[#71717A] mt-1">
              ou selectionnez depuis la galerie
            </p>
          </div>
        </div>
      </div>

      {/* Previews */}
      {files.length > 0 && (
        <div className="flex gap-3">
          {files.map((f) => (
            <div key={f.id} className="relative">
              <div className="w-20 h-20 rounded-xl overflow-hidden border border-[#27272A] bg-[#18181B]">
                <img src={f.preview} alt="Capture" className="w-full h-full object-cover" />
              </div>
              <button
                onClick={(e) => { e.stopPropagation(); removeFile(f.id) }}
                className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-[#EF4444] flex items-center justify-center"
              >
                <X className="w-3 h-3 text-white" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Progress */}
      {uploading && (
        <div className="space-y-2">
          <div className="w-full h-1.5 bg-[#27272A] rounded-full overflow-hidden">
            <div
              className="h-full bg-[#6366F1] rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-xs text-[#A1A1AA] text-center">Upload en cours... {progress}%</p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-start gap-2 text-sm text-[#EF4444]">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          {error}
        </div>
      )}

      {/* Upload button */}
      {files.length > 0 && !uploading && (
        <button
          onClick={handleUpload}
          className="w-full h-12 rounded-xl font-semibold text-sm bg-[#6366F1] hover:bg-[#818CF8] text-white flex items-center justify-center gap-2 transition-colors duration-200"
        >
          <Upload className="w-4 h-4" />
          Analyser la capture
        </button>
      )}
    </div>
  )
}

export default ScreenshotUpload
