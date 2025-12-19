import {ref} from 'vue'
import PageModal from '@/components/page-modal/page-modal.vue'

type CallbackFnType = (data: any) => void


const usePageModal = (
    newCallback?:CallbackFnType,
    editCallback?:CallbackFnType
) => {
    // 对modal组件的操作
    const modalRef = ref<InstanceType<typeof PageModal>>()
    const handleNewBtnClick = () => {
        modalRef.value?.setModalVisible()
        if (newCallback) newCallback()
    }

    const handleEditBtnClick = (itemData?: any) => {
        console.log('handleEditBtnClick', itemData)
        // 1.modal显示出来
        modalRef.value?.setModalVisible(false, itemData)
        // 2.执行回调函数
        if (editCallback) editCallback(itemData)
    }

    return {
        modalRef,
        handleNewBtnClick,
        handleEditBtnClick
    }
}


export default usePageModal