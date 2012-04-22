package Elixys.Subviews
{
	import Elixys.Assets.Constants;
	import Elixys.Extended.Input;
	import Elixys.JSON.Components.ComponentTrapF18;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This trap F18 subview is an extension of the unit operation subview class
	public class SubviewTrapF18 extends SubviewUnitOperation
	{
		/***
		 * Construction
		 **/
		
		public function SubviewTrapF18(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentTrapF18.COMPONENTTYPE, 
				SubviewUnitOperation.RUN_UNITOPERATION_ONEVIDEO, attributes);
		}
		
		// Finds the index of the specified field contents
		protected function FindIndex(pContents:*):int
		{
			for (var nIndex:int = 0; nIndex < m_pFieldContents.length; ++nIndex)
			{
				if (m_pFieldContents[nIndex] == pContents)
				{
					return nIndex;
				}
			}
			return -1;
		}
		
		// Override the input field setting function
		protected override function SetInputControl(pInput:*, pContents:*):void
		{
			// Show or hide the labels in view and edit modes based on the cyclotron flag
			var bCyclotronFlag:Boolean = Boolean(m_pComponent["CyclotronFlag"]);
			var nIndex:int = FindIndex(pInput);
			if ((m_sMode == Constants.VIEW) || (m_sMode == Constants.EDIT))
			{
				(m_pFieldLabels[nIndex] as UILabel).visible = !bCyclotronFlag;
				(m_pFieldUnits[nIndex] as UILabel).visible = !bCyclotronFlag;
				(m_pFieldErrors[nIndex] as UILabel).visible = !bCyclotronFlag;
			}

			// Show or hide the input control based on the cyclotron flag
			switch (m_sMode)
			{
				case Constants.VIEW:
					(pInput as UILabel).visible = !bCyclotronFlag;
					if (!bCyclotronFlag)
					{
						(pInput as UILabel).text = pContents.toString();
					}
					break;
				
				case Constants.EDIT:
					var pInputVar:Input = pInput as Input;
					pInputVar.visible = !bCyclotronFlag;
					if (pInputVar.inputField != m_pKeyboardFocusTextBox)
					{
						pInputVar.text = pContents.toString();
					}
					break;
			}
		}
	}
}
