import {ref} from "vue";
import PageContent from "@/components/page-content/page-content.vue";


const usePageContent = () => {
    const contentRef = ref<InstanceType<typeof PageContent>>()
    const handleQueryClick = (formData) => {
        contentRef.value?.fetchPageListData(formData)
    }

    const handleResetClick = () => {
        contentRef.value?.fetchPageListData()
    }

    return {
        contentRef,
        handleQueryClick,
        handleResetClick,
    }
}

export default usePageContent
