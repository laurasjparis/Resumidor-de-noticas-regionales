const IMAGE_FIELDS = [
  'imagen',
  'imagen_url',
  'url_imagen',
  'image',
  'image_url',
  'url_image',
  'thumbnail',
  'thumbnail_url',
  'media_url',
  'foto',
  'foto_url',
  'cover',
  'cover_image',
]

const URL_FIELDS = ['url', 'href', 'src', 'secure_url']

function normalizeImageUrl(value) {
  if (!value) return null

  if (typeof value === 'string') {
    const url = value.trim()
    if (!url || url === '#' || url === 'https://...') return null
    if (url.startsWith('/') || url.startsWith('http://') || url.startsWith('https://')) return url
    return null
  }

  if (Array.isArray(value)) {
    for (const item of value) {
      const url = normalizeImageUrl(item)
      if (url) return url
    }
    return null
  }

  if (typeof value === 'object') {
    for (const field of URL_FIELDS) {
      const url = normalizeImageUrl(value[field])
      if (url) return url
    }
  }

  return null
}

function getNestedImageUrl(item) {
  const candidates = [
    item.media,
    item.media_content,
    item.media_thumbnail,
    item.enclosure,
    item.enclosures,
    item.links?.filter((link) => link?.type?.startsWith('image/')),
  ]

  for (const candidate of candidates) {
    const url = normalizeImageUrl(candidate)
    if (url) return url
  }

  return null
}

export function getNewsImageUrl(item) {
  if (!item || typeof item !== 'object') return null

  for (const field of IMAGE_FIELDS) {
    const url = normalizeImageUrl(item[field])
    if (url) return url
  }

  const nestedUrl = getNestedImageUrl(item)
  if (nestedUrl) return nestedUrl

  if (Array.isArray(item.noticias_relacionadas)) {
    for (const related of item.noticias_relacionadas) {
      const url = getNewsImageUrl(related)
      if (url) return url
    }
  }

  return null
}
