package Elixys.Views
{
	import Elixys.Objects.*;
	
	import flash.events.EventDispatcher;
	
	import mx.collections.ArrayList;
	import mx.collections.IList;
	import mx.containers.Canvas;
	import mx.containers.TabNavigator;
	import mx.controls.Button;
	
	import spark.components.DataGrid;
	import spark.components.Group;
	import spark.components.List;
	import spark.components.VGroup;
	import spark.components.gridClasses.GridColumn;
	
	public class ViewBase extends Canvas
	{
		// Constructor
		public function ViewBase()
		{
			super();
		}
		
		// Set parent
		public function SetParent(pParent:EventDispatcher):void
		{
			m_pParent = pParent;
		}
		
		// Update functions
		public function UpdateState(pState:State):void
		{
		}
		public function UpdateSequence(pSequence:Sequence):void
		{
		}
		public function UpdateComponent(pComponent:Component):void
		{
		}
		public function UpdateReagent(pReagent:Reagent):void
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
			var nTab:uint, pTabClient:SelectSubview, pTabServer:Elixys.Objects.Tab;
			for (nTab = 0; nTab < pServerTabs.length; ++nTab)
			{
				// Either get a pointer to the existing tab or create a new one
				if (nTab < pTabNavigator.numChildren)
				{
					// Use the existing button
					pTabClient = pTabNavigator.getChildAt(nTab) as SelectSubview;
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

				// Update the tab columns
				UpdateColumns(pTabClient._sequenceGrid.columns, pTabServer.Columns());
				
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
		
		// Update the client data grid columns with the server data
		public function UpdateColumns(pColumnsClient:IList, pColumnsServer:Array):void
		{
			// Loop through the server and client data grid columns
			var nColumn:uint, pColumnClient:GridColumn, pHeadersServer:Array;
			for (nColumn = 0; nColumn < pColumnsServer.length; ++nColumn)
			{
				// Either get a pointer to the existing column or create a new one
				if (nColumn < pColumnsClient.length)
				{
					// Use the existing button
					pColumnClient = pColumnsClient.getItemAt(nColumn) as GridColumn;
				}
				else
				{
					// Create a new tab
					pColumnClient = new GridColumn();
					pColumnsClient.addItem(pColumnClient);
				}
				
				// Update the data field and header
				pHeadersServer = pColumnsServer[nColumn].split(":");
				pColumnClient.dataField = pHeadersServer[0];
				pColumnClient.headerText = pHeadersServer[1];
			}
			
			// Remove any extra tabs
			while (nColumn < pColumnsClient.length)
			{
				pColumnsClient.removeItemAt(pColumnsClient.length - 1);
			}
		}

		// Update the client sequence grid with the server data
		public function UpdateDataGrid(pDataGrid:DataGrid, pServerSequences:Array, fCreateNewSequence:Function):void
		{
			// Get a pointer to the sequence grid
			var pGridData:ArrayList;
			if (pDataGrid.dataProvider != null)
			{
				pGridData = pDataGrid.dataProvider as ArrayList;
			}
			if (pGridData == null)
			{
				pGridData = new ArrayList();
			}
		
			// Get the ID of the currently selected sequence
			var pSelectedID:String = "";
			if (pDataGrid.selectedItem)
			{
				pSelectedID = (pDataGrid.selectedItem as SequenceMetadata).ID;
			}

			// Loop through the server and client sequence arrays
			var nSequence:uint, pClientSequence:SequenceMetadata, pServerSequence:SequenceMetadata;
			for (nSequence = 0; nSequence < pServerSequences.length; ++nSequence)
			{
				// Either get a pointer to the existing sequence or create a new one
				if (nSequence < pGridData.length)
				{
					// Use the existing sequence
					pClientSequence = pGridData.getItemAt(nSequence) as SequenceMetadata;
				}
				else
				{
					// Create a new sequence
					pClientSequence = fCreateNewSequence();
					pGridData.addItem(pClientSequence);
				}
				
				// Update the sequence metadata
				pClientSequence.Copy(pServerSequences[nSequence]);
				
				// Make sure the currently selected sequence is reselected
				if (pClientSequence.ID == pSelectedID)
				{
					pDataGrid.selectedItem = pClientSequence;
				}
			}
		
			// Remove any extra sequences
			while (nSequence < pGridData.length)
			{
				pGridData.removeItemAt(pGridData.length - 1);
			}
			
			// Update the data provider
			pDataGrid.dataProvider = pGridData;
		}
		
		// Update the client list array with the server array
		public function UpdateList(pList:List, pServerItems:Array, fCreateNewItem:Function, nCurrentItemID:uint):void
		{
			// Get a pointer to the sequence data provider
			var pListData:ArrayList;
			if (pList.dataProvider != null)
			{
				pListData = pList.dataProvider as ArrayList;
			}
			if (pListData == null)
			{
				pListData = new ArrayList();
			}

			// Loop through the server and client component arrays
			var nComponent:uint, pComponentClient:SequenceComponent, pComponentServer:SequenceComponent, nNonCassetteCount:uint = 1;
			for (nComponent = 0; nComponent < pServerItems.length; ++nComponent)
			{
				// Either get a pointer to the existing component or create a new one
				if (nComponent < pListData.length)
				{
					// Use the existing component
					pComponentClient = pListData.getItemAt(nComponent) as SequenceComponent;
				}
				else
				{
					// Create a new component
					pComponentClient = fCreateNewItem();
					pListData.addItem(pComponentClient);
				}
				
				// Update the sequence component
				pComponentClient.Copy(pServerItems[nComponent]);
				if (pComponentClient.ComponentType == ComponentCassette.TYPE)
				{
					pComponentClient.DisplayIndex = 0;
				}
				else
				{
					pComponentClient.DisplayIndex = nNonCassetteCount++;
				}
				
				// Make sure the currently selected sequence is reselected
				if (pComponentClient.ID == nCurrentItemID)
				{
					pList.selectedItem = pComponentClient;
				}
			}
			
			// Remove any extra sequences
			while (nComponent < pListData.length)
			{
				pListData.removeItemAt(pListData.length - 1);
			}
			
			// Update the data provider
			pList.dataProvider = pListData;
		}
		
		/***
		 * Member variables
		 **/
		
		// Parent
		protected var m_pParent:EventDispatcher;
	}
}
