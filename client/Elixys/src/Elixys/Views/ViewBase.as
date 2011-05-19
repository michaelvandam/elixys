package Elixys.Views
{
	import Elixys.Objects.Button;
	import Elixys.Objects.SequenceMetadata;
	import Elixys.Objects.State;
	
	import mx.collections.ArrayList;
	import mx.containers.Canvas;
	import mx.containers.TabNavigator;
	import mx.controls.Button;
	
	import spark.components.Group;
	import spark.components.List;
	import spark.components.VGroup;
	
	public class ViewBase extends Canvas
	{
		// Constructor
		public function ViewBase()
		{
			super();
		}
		
		// Update function
		public function Update(pState:State):void
		{
		}
		
		// Update the client button array with the server array
		public function UpdateButtons(pClientButtons:Group, pServerButtons:Array, fCreateNewButton:Function):void
		{
			// Loop through the server and client button arrays
			var nButton:uint, pButtonClient:spark.components.Button, pButtonServer:Elixys.Objects.Button;
			for (nButton = 0; nButton < pServerButtons.length; ++nButton)
			{
				// Either get a pointer to the existing button or create a new one
				if (nButton < pClientButtons.numElements)
				{
					// Use the existing button
					pButtonClient = pClientButtons.getElementAt(nButton) as spark.components.Button;
				}
				else
				{
					// Create a new button
					pButtonClient = fCreateNewButton();
					pClientButtons.addElement(pButtonClient);
				}
			
				// Update the button text and ID
				pButtonServer = pServerButtons[nButton];
				pButtonClient.label = pButtonServer.Text();
				pButtonClient.id = pButtonServer.ID();
			}
		
			// Remove any extra buttons
			while (nButton < pClientButtons.numElements)
			{
				pClientButtons.removeElementAt(pClientButtons.numElements - 1);
			}
		}

		// Update the client tab array with the server array
		public function UpdateTabs(pTabNavigator:TabNavigator, pServerTabs:Array, fCreateNewTab:Function, sCurrentTabID:String):void
		{
			// Loop through the server and client tab arrays
			var nTab:uint, pTabClient:SelectViewTab, pTabServer:Elixys.Objects.Tab;
			for (nTab = 0; nTab < pServerTabs.length; ++nTab)
			{
				// Either get a pointer to the existing tab or create a new one
				if (nTab < pTabNavigator.numChildren)
				{
					// Use the existing button
					pTabClient = pTabNavigator.getChildAt(nTab) as SelectViewTab;
				}
				else
				{
					// Create a new tab
					pTabClient = fCreateNewTab();
					pTabNavigator.addChild(pTabClient);
				}
			
				// Update the tab label and ID
				pTabServer = pServerTabs[nTab];
				pTabClient.label = pTabServer.Text();
				pTabClient.id = pTabServer.ID();
			
				// Select the current tab
				if (pTabClient.id == sCurrentTabID)
				{
					pTabNavigator.selectedChild = pTabClient;
				}
			}
		
			// Remove any extra tabs
			while (nTab < pTabNavigator.numChildren)
			{
				pTabNavigator.removeChildAt(pTabNavigator.numChildren - 1);
			}
		}
		
		// Update the client sequence list with the server list
		public function UpdateList(pList:List, pServerSequences:Array, fCreateNewSequence:Function):void
		{
			// Get a pointer to the sequence list
			var pListData:ArrayList;
			if (pList.dataProvider != null)
			{
				pListData = pList.dataProvider as ArrayList;
			}
			if (pListData == null)
			{
				pListData = new ArrayList();
			}
		
			// Get the ID of the currently selected sequence
			var pSelectedID:String = "";
			if (pList.selectedItem != undefined)
			{
				pSelectedID = (pList.selectedItem as SequenceMetadata).ID();
			}

			// Loop through the server and client sequence arrays
			var nSequence:uint, pClientSequence:SequenceMetadata, pServerSequence:SequenceMetadata;
			for (nSequence = 0; nSequence < pServerSequences.length; ++nSequence)
			{
				// Either get a pointer to the existing sequence or create a new one
				if (nSequence < pListData.length)
				{
					// Use the existing sequence
					pClientSequence = pListData.getItemAt(nSequence) as SequenceMetadata;
				}
				else
				{
					// Create a new sequence
					pClientSequence = fCreateNewSequence();
					pListData.addItem(pClientSequence);
				}
				
				// Update the sequence metadata
				pClientSequence.Copy(pServerSequences[nSequence]);
				
				// Make sure the currently selected sequence is reselected
				if (pClientSequence.ID() == pSelectedID)
				{
					pList.selectedItem = pClientSequence;
				}
			}
		
			// Remove any extra sequences
			while (nSequence < pListData.length)
			{
				pListData.removeItemAt(pListData.length - 1);
			}
			
			// Update the sequence list
			pList.dataProvider = pListData;
		}
	}
}
