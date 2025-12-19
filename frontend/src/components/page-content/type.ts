export interface IContentProps {
  contentConfig: {
    pageName: string
    header?: {
      title?: string
      btnTitle?: string
    },
    propsList: any[]
  }
}