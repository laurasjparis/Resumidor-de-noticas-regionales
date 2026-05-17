import { useState } from 'react'
import { getNewsImageUrl } from '../utils/newsImages'

export default function NewsImage({ item, alt, wrapperClassName, imageClassName }) {
  const [failedUrl, setFailedUrl] = useState(null)
  const imageUrl = getNewsImageUrl(item)

  if (!imageUrl || imageUrl === failedUrl) return null

  return (
    <div className={wrapperClassName}>
      <img
        src={imageUrl}
        alt={alt || item?.titulo || 'Imagen de la noticia'}
        className={imageClassName}
        loading="lazy"
        onError={() => setFailedUrl(imageUrl)}
      />
    </div>
  )
}
