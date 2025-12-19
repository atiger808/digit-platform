interface MenuItemType {
  id: string
  name: string
  path: string
  icon?: string
  meta?: { title: string }
  children?: MenuItemType[]
}